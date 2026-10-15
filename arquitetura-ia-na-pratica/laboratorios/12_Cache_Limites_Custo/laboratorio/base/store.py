"""Offline teaching repository. Administrative methods are trusted, not HTTP APIs."""
from contextlib import contextmanager
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import json
import sqlite3

POLICY = 'acl-v1'

def fingerprint(value):
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True)
    return sha256(raw.encode('utf-8')).hexdigest()

@dataclass(frozen=True)
class Actor:
    tenant: str
    user: str

@dataclass(frozen=True)
class Snapshot:
    tenant: str
    user: str
    document: str
    version: int
    sequence: int
    epoch: int
    role: str
    language: str
    body: str
    digest: str
    source: str
    policy: str = POLICY

def cache_key(snapshot):
    return (
        snapshot.tenant, snapshot.user,
        snapshot.document, snapshot.language,
        snapshot.version, snapshot.sequence,
        snapshot.epoch, snapshot.role,
        snapshot.policy, snapshot.digest,
    )

class Conflict(Exception):
    pass

class Store:
    def __init__(self, path=':memory:'):
        self.db = sqlite3.connect(path, isolation_level=None)
        self.db.row_factory = sqlite3.Row
        self.db.executescript(Path(__file__).with_name('schema.sql').read_text())

    def close(self):
        self.db.close()

    @contextmanager
    def transaction(self):
        self.db.execute('BEGIN IMMEDIATE')
        try:
            yield
            self.db.execute('COMMIT')
        except BaseException:
            self.db.execute('ROLLBACK')
            raise

    def bump(self, tenant):
        self.db.execute('INSERT INTO epochs VALUES (?,1) '
                        'ON CONFLICT(tenant) DO UPDATE SET epoch=epoch+1', (tenant,))

    def principal(self, tenant, user, role, active=True):
        with self.transaction():
            self.db.execute('INSERT INTO principals VALUES (?,?,?,?) '
                            'ON CONFLICT(tenant,user_id) DO UPDATE SET '
                            'role=excluded.role,active=excluded.active',
                            (tenant, user, role, int(active)))
            self.bump(tenant)

    def publish(self, tenant, doc, pt, en, source, roles,
                expected, request_id, fail=False):
        if not pt.strip() or not en.strip() or not source.strip():
            raise ValueError('body and provenance required')
        roles = sorted(set(roles))
        payload = fingerprint([doc, pt, en, source, roles, expected])
        content_hash = fingerprint([pt, en, source])
        with self.transaction():
            previous = self.db.execute(
                'SELECT * FROM commands WHERE tenant=? AND request_id=?',
                (tenant, request_id)).fetchone()
            if previous:
                if previous['payload_hash'] != payload:
                    raise Conflict('idempotency key reused with different payload')
                return previous['result_version']
            current = self.db.execute(
                'SELECT * FROM documents WHERE tenant=? AND doc_id=?',
                (tenant, doc)).fetchone()
            if current and current['deleted']:
                raise Conflict('tombstone cannot be republished')
            version = current['active_version'] if current else 0
            if version != expected:
                raise Conflict('stale expected version')
            version += 1
            seq = current['seq']+1 if current else 1
            if current:
                self.db.execute('UPDATE documents SET active_version=?,seq=? '
                                'WHERE tenant=? AND doc_id=?',
                                (version, seq, tenant, doc))
            else:
                self.db.execute('INSERT INTO documents '
                                '(tenant,doc_id,active_version,seq) VALUES (?,?,?,?)',
                                (tenant, doc, version, seq))
            self.db.execute('INSERT INTO versions VALUES (?,?,?,?,?,?,?)',
                            (tenant, doc, version, pt, en, source, content_hash))
            self.db.execute('DELETE FROM acl WHERE tenant=? AND doc_id=?', (tenant, doc))
            self.db.executemany('INSERT INTO acl VALUES (?,?,?)',
                                [(tenant, doc, role) for role in roles])
            self.db.execute('INSERT INTO outbox (tenant,doc_id,seq) VALUES (?,?,?)',
                            (tenant, doc, seq))
            self.bump(tenant)
            if fail:
                raise RuntimeError('injected failure before commit')
            self.db.execute('INSERT INTO commands VALUES (?,?,?,?)',
                            (tenant, request_id, payload, version))
        return version

    def set_acl(self, tenant, doc, roles):
        with self.transaction():
            row = self.db.execute('SELECT deleted FROM documents '
                                  'WHERE tenant=? AND doc_id=?', (tenant, doc)).fetchone()
            if not row or row['deleted']:
                raise Conflict('unavailable document')
            self.db.execute('DELETE FROM acl WHERE tenant=? AND doc_id=?', (tenant, doc))
            self.db.executemany('INSERT INTO acl VALUES (?,?,?)',
                               [(tenant, doc, r) for r in sorted(set(roles))])
            self.bump(tenant)

    def process(self, event_id, replay=False, fail=False):
        with self.transaction():
            event = self.db.execute('SELECT * FROM outbox WHERE event_id=?',
                                     (event_id,)).fetchone()
            if not event:
                raise KeyError(event_id)
            if event['done'] and not replay:
                return 'duplicate'
            scope = (event['tenant'], event['doc_id'])
            current = self.db.execute('SELECT * FROM documents '
                                      'WHERE tenant=? AND doc_id=?', scope).fetchone()
            if current['deleted']:
                self.db.execute('DELETE FROM projection WHERE tenant=? AND doc_id=?', scope)
            else:
                version = self.db.execute('SELECT digest FROM versions '
                    'WHERE tenant=? AND doc_id=? AND version=?',
                    (*scope, current['active_version'])).fetchone()
                self.db.execute('INSERT INTO projection VALUES (?,?,?,?,?) '
                    'ON CONFLICT(tenant,doc_id) DO UPDATE SET version=excluded.version,'
                    'seq=excluded.seq,digest=excluded.digest',
                    (*scope, current['active_version'], current['seq'], version['digest']))
            if fail:
                raise RuntimeError('injected worker failure before acknowledgment')
            self.db.execute('UPDATE outbox SET done=1 WHERE event_id=?', (event_id,))
        return 'processed'

    def drain(self):
        ids = [r[0] for r in self.db.execute(
            'SELECT event_id FROM outbox WHERE done=0 ORDER BY event_id')]
        for event_id in ids:
            self.process(event_id)
        return len(ids)

    def prepare(self, actor, doc, language):
        if language not in ('pt-BR', 'en-US'):
            raise ValueError('unsupported language')
        row = self.db.execute('''
          SELECT v.*,d.seq,e.epoch,p.role
          FROM documents d
          JOIN versions v ON v.tenant=d.tenant AND v.doc_id=d.doc_id
                         AND v.version=d.active_version
          JOIN principals p ON p.tenant=d.tenant AND p.user_id=? AND p.active=1
          JOIN acl a ON a.tenant=d.tenant AND a.doc_id=d.doc_id AND a.role=p.role
          JOIN epochs e ON e.tenant=d.tenant
          JOIN projection x ON x.tenant=d.tenant AND x.doc_id=d.doc_id
                           AND x.version=d.active_version AND x.seq=d.seq
                           AND x.digest=v.digest
          WHERE d.tenant=? AND d.doc_id=? AND d.deleted=0
        ''', (actor.user, actor.tenant, doc)).fetchone()
        if not row:
            return None
        if fingerprint([row['body_pt'], row['body_en'], row['source_uri']]) != row['digest']:
            return None
        body = row['body_pt' if language == 'pt-BR' else 'body_en']
        return Snapshot(actor.tenant, actor.user, doc, row['version'], row['seq'],
                        row['epoch'], row['role'], language, body,
                        row['digest'], row['source_uri'])

    def still_current(self, snapshot):
        current = self.prepare(
            Actor(snapshot.tenant, snapshot.user),
            snapshot.document, snapshot.language,
        )
        return current == snapshot

    def delete(self, tenant, doc, day, retention_days):
        if retention_days < 0:
            raise ValueError('negative retention')
        with self.transaction():
            row = self.db.execute('SELECT * FROM documents WHERE tenant=? AND doc_id=?',
                                   (tenant, doc)).fetchone()
            if not row or row['deleted']:
                return False
            seq = row['seq']+1
            self.db.execute('UPDATE documents SET deleted=1,seq=?,purge_at=? '
                            'WHERE tenant=? AND doc_id=?',
                            (seq, day+retention_days, tenant, doc))
            self.db.execute('INSERT INTO outbox(tenant,doc_id,seq) VALUES (?,?,?)',
                            (tenant, doc, seq))
            self.bump(tenant)
        return True

    def purge(self, day):
        with self.transaction():
            docs = self.db.execute('SELECT tenant,doc_id FROM documents '
                'WHERE deleted=1 AND purge_at IS NOT NULL AND purge_at<=?', (day,)).fetchall()
            for row in docs:
                scope = tuple(row)
                for table in ('versions', 'acl', 'projection'):
                    self.db.execute(f'DELETE FROM {table} WHERE tenant=? AND doc_id=?', scope)
                self.db.execute('UPDATE documents SET purge_at=NULL '
                                'WHERE tenant=? AND doc_id=?', scope)
        return len(docs)

class Copilot:
    """Extractive stand-in, not an LLM. Cache contains synthetic answer strings."""
    def __init__(self, store):
        self.store = store
        self.cache = {}
        self.generations = 0

    def answer(self, actor, doc, language='pt-BR', between=None):
        snapshot = self.store.prepare(actor, doc, language)
        unavailable = {'status':'unavailable','answer':None,'citations':[],'cached':False}
        if snapshot is None:
            return unavailable
        key = cache_key(snapshot)
        cached = key in self.cache
        if not cached:
            self.generations += 1
        text = self.cache.get(key, snapshot.body)
        if between:
            between()
        if not self.store.still_current(snapshot):
            return unavailable
        self.cache[key] = text
        citation = {'document':doc,'version':snapshot.version,
                    'digest':snapshot.digest,'source':snapshot.source}
        return {'status':'answer','answer':text,'citations':[citation],'cached':cached}
