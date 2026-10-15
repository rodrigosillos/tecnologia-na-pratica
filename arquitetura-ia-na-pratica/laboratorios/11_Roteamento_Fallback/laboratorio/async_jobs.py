"""Durable local job model. Independent SQLite queue; no HTTP or external effects."""
from contextlib import contextmanager
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import json
import sqlite3
from resilience import integer

TERMINAL = {'succeeded', 'failed', 'cancelled', 'expired'}
OPERATION = 'compare-manuals-v1'


class IdempotencyConflict(ValueError): pass
class LeaseLost(RuntimeError): pass
class Crash(RuntimeError): pass


def canonical_payload(payload):
    if type(payload) is not dict or set(payload) != {'language', 'documents'}:
        raise ValueError('payload fields')
    if payload['language'] not in ('pt-BR', 'en-US'):
        raise ValueError('language')
    docs = payload['documents']
    if type(docs) is not list or len(docs) != 2:
        raise ValueError('two document IDs required')
    if any(type(d) is not str or not 0 < len(d) <= 80 for d in docs):
        raise ValueError('document IDs')
    if docs[0] == docs[1]:
        raise ValueError('distinct manuals required')
    return json.dumps(payload, ensure_ascii=False,
                      sort_keys=True, separators=(',', ':'))


def request_fingerprint(payload):
    raw = OPERATION + '\n' + canonical_payload(payload)
    return sha256(raw.encode('utf-8')).hexdigest()


@contextmanager
def transaction(db):
    db.execute('BEGIN IMMEDIATE')
    try:
        yield
        db.execute('COMMIT')
    except BaseException:
        db.execute('ROLLBACK')
        raise


def connect(path):
    db = sqlite3.connect(str(path), isolation_level=None, timeout=5)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA foreign_keys=ON')
    db.execute('PRAGMA synchronous=FULL')
    return db


@dataclass(frozen=True)
class JobLease:
    job_id: int
    generation: int
    worker: str


class Jobs:
    def __init__(self, path=':memory:'):
        self.db = connect(path)
        self.db.executescript(Path(__file__).with_name('jobs.sql').read_text())

    def close(self): self.db.close()

    def job(self, job_id):
        row = self.db.execute('SELECT * FROM jobs WHERE id=?', (job_id,)).fetchone()
        return dict(row) if row else None

    def submit(self, actor, key, payload, now, validity_ms=2000,
               crash_before_commit=False):
        integer(now, 'now'); integer(validity_ms, 'validity_ms', 1)
        if type(key) is not str or not 1 <= len(key) <= 100:
            raise ValueError('idempotency key')
        raw = canonical_payload(payload)
        digest = request_fingerprint(payload)
        with transaction(self.db):
            row = self.db.execute('''SELECT * FROM jobs WHERE
                tenant=? AND subject=? AND operation=? AND idem_key=?''',
                (actor.tenant, actor.user, OPERATION, key)).fetchone()
            if row:
                if row['fingerprint'] != digest:
                    raise IdempotencyConflict('key reused for another intent')
                return dict(job_id=row['id'], status=200, replay=True,
                            location=f"/jobs/{row['id']}")
            cur = self.db.execute('''INSERT INTO jobs
                (tenant,subject,operation,idem_key,fingerprint,payload,
                 state,created_ms,deadline_ms,next_ms)
                VALUES (?,?,?,?,?,?,'queued',?,?,?)''',
                (actor.tenant,actor.user,OPERATION,key, digest,raw,
                 now,now+validity_ms,now))
            job_id = cur.lastrowid
            self.db.execute('INSERT INTO dispatch_outbox(job_id) VALUES (?)',
                            (job_id,))
            if crash_before_commit:
                raise Crash('before acceptance commit')
        return dict(job_id=job_id, status=202, replay=False,
                    location=f'/jobs/{job_id}')

    def relay(self, queue, now, crash_after_publish=False):
        rows = self.db.execute('SELECT * FROM dispatch_outbox WHERE sent=0 ORDER BY event_id').fetchall()
        for row in rows:
            queue.publish(row['event_id'], row['job_id'], now)
            if crash_after_publish:
                raise Crash('published but not marked sent')
            with transaction(self.db):
                self.db.execute('UPDATE dispatch_outbox SET sent=1 WHERE event_id=?',
                                (row['event_id'],))
        return len(rows)

    def _terminal(self, job_id, state, reason=None):
        self.db.execute('''UPDATE jobs SET state=?,error_code=?,worker=NULL,
            lease_until=0,generation=generation+1 WHERE id=?''',
            (state,reason,job_id))
        if state == 'failed':
            self.db.execute('''INSERT OR IGNORE INTO dead_letters
                SELECT id,?,attempts FROM jobs WHERE id=?''',(reason,job_id))

    def expire(self, now):
        integer(now,'now')
        with transaction(self.db):
            rows = self.db.execute("SELECT id FROM jobs WHERE deadline_ms<=? AND state IN ('queued','running','retry_wait')",(now,)).fetchall()
            for row in rows: self._terminal(row['id'],'expired','deadline')

    def claim(self, job_id, worker, now, lease_ms=100, max_attempts=3):
        integer(now,'now');integer(lease_ms,'lease_ms',1)
        integer(max_attempts,'max_attempts',1)
        if not isinstance(worker,str) or not worker: raise ValueError('worker')
        self.expire(now)
        with transaction(self.db):
            row = self.job(job_id)
            if row is None or row['state'] in TERMINAL: return None
            if row['state']=='running' and row['lease_until']>now: return None
            if row['next_ms']>now: return None
            if row['attempts']>=max_attempts:
                self._terminal(job_id,'failed','attempt_limit');return None
            generation = row['generation']+1
            self.db.execute('''UPDATE jobs SET state='running',worker=?,
                generation=?,lease_until=?,attempts=attempts+1 WHERE id=?''',
                (worker,generation,min(now+lease_ms,row['deadline_ms']),job_id))
            return JobLease(job_id,generation,worker)

    def _guard(self, lease, now):
        integer(now,'now')
        row = self.job(lease.job_id)
        if (row is None or row['state']!='running' or
            row['worker']!=lease.worker or row['generation']!=lease.generation or
            row['lease_until']<=now or row['deadline_ms']<=now):
            raise LeaseLost('lease no longer authorizes a write')
        return row

    def heartbeat(self, lease, now, lease_ms=100):
        integer(lease_ms,'lease_ms',1)
        with transaction(self.db):
            row=self._guard(lease,now)
            self.db.execute('UPDATE jobs SET lease_until=? WHERE id=?',
                (min(now+lease_ms,row['deadline_ms']),lease.job_id))

    def saved(self, job_id):
        return [json.loads(r['value']) for r in self.db.execute(
            'SELECT value FROM checkpoints WHERE job_id=? ORDER BY position',(job_id,))]

    def checkpoint(self, lease, position, value, now, crash=False):
        with transaction(self.db):
            row=self._guard(lease,now)
            if type(position) is not int or position != row['stage'] or position>=2:
                raise ValueError('checkpoint must advance exactly one stage')
            self.db.execute('INSERT INTO checkpoints VALUES (?,?,?)',
                (lease.job_id,position,json.dumps(value,sort_keys=True)))
            self.db.execute('UPDATE jobs SET stage=stage+1 WHERE id=?',(lease.job_id,))
            if crash: raise Crash('checkpoint before commit')

    def complete(self, lease, result, now, crash=False):
        with transaction(self.db):
            row=self._guard(lease,now)
            if row['stage'] != 2: raise ValueError('incomplete work')
            self.db.execute('INSERT INTO job_results VALUES (?,?)',
                (lease.job_id,json.dumps(result,sort_keys=True)))
            self._terminal(lease.job_id,'succeeded')
            if crash: raise Crash('result before commit')

    def fail(self, lease, now, transient=True, delay_ms=200, max_attempts=3):
        integer(delay_ms,'delay_ms');integer(max_attempts,'max_attempts',1)
        with transaction(self.db):
            row=self._guard(lease,now)
            if not transient or row['attempts']>=max_attempts:
                self._terminal(lease.job_id,'failed',
                               'attempt_limit' if transient else 'source_changed')
            elif now+delay_ms>=row['deadline_ms']:
                self._terminal(lease.job_id,'expired','retry_outside_deadline')
            else:
                self.db.execute('''UPDATE jobs SET state='retry_wait',next_ms=?,
                    worker=NULL,lease_until=0,generation=generation+1 WHERE id=?''',
                    (now+delay_ms,lease.job_id))

    def cancel(self, actor, job_id):
        with transaction(self.db):
            row=self.job(job_id)
            if not row or (row['tenant'],row['subject'])!=(actor.tenant,actor.user):
                return False
            if row['state'] in TERMINAL: return False
            self.db.execute('UPDATE jobs SET cancel_requested=1 WHERE id=?',(job_id,))
            self._terminal(job_id,'cancelled')
            return True


@dataclass(frozen=True)
class Receipt:
    message_id: int
    generation: int
    event_id: int
    job_id: int


class LocalQueue:
    """A second durable DB simulates broker visibility and acknowledgement."""
    def __init__(self, path=':memory:'):
        self.db=connect(path)
        self.db.execute('''CREATE TABLE IF NOT EXISTS messages (
          id INTEGER PRIMARY KEY AUTOINCREMENT,event_id INTEGER NOT NULL,
          job_id INTEGER NOT NULL,visible_ms INTEGER NOT NULL,
          generation INTEGER NOT NULL DEFAULT 0,acked INTEGER NOT NULL DEFAULT 0)''')

    def close(self): self.db.close()

    def publish(self, event_id, job_id, now):
        integer(now,'now')
        with transaction(self.db):
            self.db.execute('INSERT INTO messages(event_id,job_id,visible_ms) VALUES (?,?,?)',
                            (event_id,job_id,now))

    def receive(self, now, visibility_ms=100):
        integer(now,'now');integer(visibility_ms,'visibility_ms',1)
        with transaction(self.db):
            row=self.db.execute('''SELECT * FROM messages WHERE acked=0 AND
                visible_ms<=? ORDER BY id LIMIT 1''',(now,)).fetchone()
            if not row:return None
            generation=row['generation']+1
            self.db.execute('UPDATE messages SET visible_ms=?,generation=? WHERE id=?',
                            (now+visibility_ms,generation,row['id']))
            return Receipt(row['id'],generation,row['event_id'],row['job_id'])

    def ack(self, receipt, now):
        integer(now,'now')
        with transaction(self.db):
            return self.db.execute('''UPDATE messages SET acked=1 WHERE
                id=? AND generation=? AND acked=0 AND visible_ms>?''',
                (receipt.message_id,receipt.generation,now)).rowcount==1

    def pending(self):
        return self.db.execute('SELECT count(*) FROM messages WHERE acked=0').fetchone()[0]
