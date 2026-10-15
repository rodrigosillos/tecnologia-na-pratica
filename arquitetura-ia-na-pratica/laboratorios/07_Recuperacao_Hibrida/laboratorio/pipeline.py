"""Recoverable local ingestion; administrative calls require a trusted caller."""
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import json
import unicodedata
from base.store import Store, Actor, Copilot, Conflict, fingerprint

MAX_BYTES = 8192
MAX_CHARACTERS = 6000
MAX_CLAIMS = 3
LANGUAGES = ('pt-BR', 'en-US')
DEFAULT_CONFIG = {'extractor':'json-nfc-v1','chunker':'chars-v1',
                  'size':72,'overlap':12}

def chunk_text(text, size, overlap):
    if not 0 <= overlap < size:
        raise ValueError('invalid overlap')
    start = 0
    chunks = []
    while start < len(text):
        stop = min(start + size, len(text))
        chunks.append((start, stop, text[start:stop]))
        if stop == len(text):
            break
        start = stop - overlap
    return chunks

def extract(raw):
    def unique(pairs):
        result = {}
        for key,value in pairs:
            if key in result:
                raise ValueError('duplicate field')
            result[key] = value
        return result
    data = json.loads(raw.decode('utf-8'), object_pairs_hook=unique)
    if not isinstance(data,dict) or set(data) != set(LANGUAGES):
        raise ValueError('expected two language fields')
    result = {}
    for language in LANGUAGES:
        if not isinstance(data[language],str):
            raise ValueError('body must be text')
        value = data[language].replace('\r\n','\n').replace('\r','\n')
        value = unicodedata.normalize('NFC',value).strip()
        if not value or len(value)>MAX_CHARACTERS or '\x00' in value:
            raise ValueError('invalid body')
        result[language] = value
    return result

def plan(job):
    texts=json.loads(job['normalized']);cfg=json.loads(job['config'])
    rows=[]
    for language in LANGUAGES:
        pieces=chunk_text(texts[language],cfg['size'],cfg['overlap'])
        for ordinal,(start,stop,body) in enumerate(pieces):
            digest=sha256(body.encode('utf-8')).hexdigest()
            cid=fingerprint([job['job_id'],language,ordinal,start,stop,digest])
            rows.append([language,ordinal,start,stop,body,digest,cid])
    return rows

@dataclass(frozen=True)
class Lease:
    job: str
    owner: str
    token: int

class LostLease(Exception):
    pass

class Pipeline(Store):
    def __init__(self,path=':memory:'):
        super().__init__(path)
        self.db.executescript(Path(__file__).with_name('ingestion.sql').read_text())

    def job(self,job_id):
        row=self.db.execute('SELECT * FROM jobs WHERE job_id=?',(job_id,)).fetchone()
        if row is None:raise KeyError(job_id)
        return dict(row)

    def submit(self,tenant,doc,raw,source,roles,expected,request_id,config=None):
        cfg=dict(DEFAULT_CONFIG if config is None else config)
        if set(cfg)!=set(DEFAULT_CONFIG) or cfg['extractor']!='json-nfc-v1' or cfg['chunker']!='chars-v1':
            raise ValueError('unsupported configuration')
        if type(cfg['size']) is not int or type(cfg['overlap']) is not int:
            raise ValueError('integer sizes required')
        if not 8<=cfg['size']<=1024 or not 0<=cfg['overlap']<cfg['size']:
            raise ValueError('invalid chunk window')
        if not isinstance(raw,bytes) or not 0<len(raw)<=MAX_BYTES:
            raise ValueError('source byte limit')
        if not all(isinstance(x,str) and x.strip() for x in (tenant,doc,source,request_id)):
            raise ValueError('identity and provenance required')
        if type(expected) is not int or expected < 0:
            raise ValueError('nonnegative expected version required')
        if not isinstance(roles,(list,tuple)) or any(not isinstance(r,str) or not r.strip() for r in roles):
            raise ValueError('roles must be a list of nonempty strings')
        roles=sorted(set(roles));raw_hash=sha256(raw).hexdigest()
        payload=fingerprint([doc,raw_hash,source,roles,expected,cfg])
        jid=fingerprint([tenant,request_id])
        with self.transaction():
            old=self.db.execute('SELECT * FROM jobs WHERE tenant=? AND request_id=?',
                                (tenant,request_id)).fetchone()
            if old:
                if old['payload_hash']!=payload:raise Conflict('key reused')
                return old['job_id']
            epoch=self.db.execute('SELECT epoch FROM epochs WHERE tenant=?',(tenant,)).fetchone()
            self.db.execute('''INSERT INTO jobs
              (job_id,tenant,doc_id,request_id,payload_hash,raw,raw_hash,source_uri,
               roles,expected,base_epoch,config) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''',
              (jid,tenant,doc,request_id,payload,raw,raw_hash,source,
               json.dumps(roles),expected,epoch[0] if epoch else 0,json.dumps(cfg)))
        return jid

    def claim(self,job_id,owner,now,ttl=10):
        if not owner or ttl<=0:raise ValueError('owner and positive ttl required')
        with self.transaction():
            job=self.job(job_id)
            if job['state'] in ('published','quarantined','obsolete'):return None
            if job['owner'] and job['lease_until']>now:return None
            if job['claims']>=MAX_CLAIMS:
                self.db.execute("UPDATE jobs SET state='quarantined',error='claim_budget',owner=NULL,lease_until=NULL WHERE job_id=?",(job_id,))
                return None
            token=job['token']+1
            self.db.execute('UPDATE jobs SET owner=?,token=?,lease_until=?,claims=claims+1 WHERE job_id=?',
                            (owner,token,now+ttl,job_id))
        return Lease(job_id,owner,token)

    def leased(self,lease,now):
        job=self.job(lease.job)
        if (job['owner']!=lease.owner or job['token']!=lease.token
            or job['lease_until'] is None or now>=job['lease_until']
            or job['state'] not in ('queued','staging','ready')):
            raise LostLease('expired or superseded lease')
        return job

    def renew(self,lease,now,ttl=10):
        if ttl<=0:raise ValueError('positive ttl required')
        with self.transaction():
            self.leased(lease,now)
            self.db.execute('UPDATE jobs SET lease_until=? WHERE job_id=?',(now+ttl,lease.job))

    def quarantine(self,job_id,reason):
        self.db.execute("UPDATE jobs SET state='quarantined',error=?,owner=NULL,lease_until=NULL WHERE job_id=?",(reason,job_id))

    def prepare_job(self,lease,now):
        with self.transaction():
            job=self.leased(lease,now)
            if job['state']!='queued':return job['state']
            try:
                if sha256(job['raw']).hexdigest()!=job['raw_hash']:
                    raise ValueError('source digest mismatch')
                normalized=json.dumps(extract(job['raw']),ensure_ascii=False)
            except (ValueError,UnicodeError):
                self.quarantine(lease.job,'invalid_source')
                return 'quarantined'
            job['normalized']=normalized
            rows=plan(job)
            self.db.execute("UPDATE jobs SET normalized=?,total=?,manifest=?,state='staging' WHERE job_id=?",
                            (normalized,len(rows),fingerprint(rows),lease.job))
        return 'staging'

    def write_batch(self,lease,now,size=2,fail=False):
        if type(size) is not int or not 1<=size<=100:raise ValueError('invalid batch size')
        with self.transaction():
            job=self.leased(lease,now)
            if job['state']=='ready':return 0
            if job['state']!='staging':raise Conflict('extract first')
            rows=plan(job)
            if fingerprint(rows)!=job['manifest']:
                self.quarantine(lease.job,'plan_changed');return 0
            batch=rows[job['cursor']:job['cursor']+size]
            for row in batch:
                self.db.execute('INSERT INTO chunks VALUES (?,?,?,?,?,?,?,?)',(lease.job,*row))
            cursor=job['cursor']+len(batch)
            state='ready' if cursor==job['total'] else 'staging'
            self.db.execute('UPDATE jobs SET cursor=?,state=? WHERE job_id=?',(cursor,state,lease.job))
            if fail:raise RuntimeError('crash before batch commit')
        return len(batch)

    def activate(self,lease,now,fail=False):
        with self.transaction():
            job=self.job(lease.job)
            if job['state']=='published':return job['result_version']
            job=self.leased(lease,now)
            if job['state']!='ready':raise Conflict('incomplete generation')
            expected_rows=plan(job)
            rows=[list(r) for r in self.db.execute('''SELECT language,ordinal,start,stop,body,digest,chunk_id
                   FROM chunks WHERE job_id=? ORDER BY CASE language WHEN 'pt-BR' THEN 0 ELSE 1 END,ordinal''',(lease.job,))]
            if (rows!=expected_rows or len(rows)!=job['total']
                or fingerprint(rows)!=job['manifest']):
                self.quarantine(lease.job,'chunk_integrity');return None
            scope=(job['tenant'],job['doc_id'])
            current=self.db.execute('SELECT * FROM documents WHERE tenant=? AND doc_id=?',scope).fetchone()
            epoch=self.db.execute('SELECT epoch FROM epochs WHERE tenant=?',(scope[0],)).fetchone()
            version=current['active_version'] if current else 0
            if ((current and current['deleted']) or version!=job['expected']
                or (epoch[0] if epoch else 0)!=job['base_epoch']):
                self.db.execute("UPDATE jobs SET state='obsolete',owner=NULL,lease_until=NULL,error='base_changed' WHERE job_id=?",(lease.job,))
                return None
            texts=json.loads(job['normalized']);version+=1
            seq=current['seq']+1 if current else 1
            if current:
                self.db.execute('UPDATE documents SET active_version=?,seq=? WHERE tenant=? AND doc_id=?',(version,seq,*scope))
            else:
                self.db.execute('INSERT INTO documents(tenant,doc_id,active_version,seq) VALUES (?,?,?,?)',(*scope,version,seq))
            pt,en=(texts[k] for k in LANGUAGES)
            self.db.execute('INSERT INTO versions VALUES (?,?,?,?,?,?,?)',
                            (*scope,version,pt,en,job['source_uri'],fingerprint([pt,en,job['source_uri']])))
            self.db.execute('DELETE FROM acl WHERE tenant=? AND doc_id=?',scope)
            self.db.executemany('INSERT INTO acl VALUES (?,?,?)',[(*scope,r) for r in json.loads(job['roles'])])
            self.db.execute('INSERT INTO outbox(tenant,doc_id,seq) VALUES (?,?,?)',(*scope,seq))
            self.bump(scope[0])
            self.db.execute('INSERT INTO heads VALUES (?,?,?,?) ON CONFLICT(tenant,doc_id) DO UPDATE SET job_id=excluded.job_id,version=excluded.version',(*scope,lease.job,version))
            self.db.execute("UPDATE jobs SET state='published',result_version=?,owner=NULL,lease_until=NULL WHERE job_id=?",(version,lease.job))
            if fail:raise RuntimeError('crash before activation commit')
        return version

    def visible_chunks(self,actor,doc,language='pt-BR'):
        snap=self.prepare(actor,doc,language)
        if snap is None:return []
        head=self.db.execute('SELECT * FROM heads WHERE tenant=? AND doc_id=? AND version=?',
                             (actor.tenant,doc,snap.version)).fetchone()
        if head is None:return []
        rows=[dict(r) for r in self.db.execute('SELECT * FROM chunks WHERE job_id=? AND language=? ORDER BY ordinal',
                                              (head['job_id'],language))]
        return rows if self.still_current(snap) else []

    def purge(self,day):
        # Extend Chapter 5 deletion to local raw, staging and job records.
        with self.transaction():
            scopes=[tuple(r) for r in self.db.execute('SELECT tenant,doc_id FROM documents WHERE deleted=1 AND purge_at IS NOT NULL AND purge_at<=?',(day,))]
            for scope in scopes:
                ids=[r[0] for r in self.db.execute('SELECT job_id FROM jobs WHERE tenant=? AND doc_id=?',scope)]
                self.db.execute('DELETE FROM heads WHERE tenant=? AND doc_id=?',scope)
                for jid in ids:
                    self.db.execute('DELETE FROM chunks WHERE job_id=?',(jid,))
                    self.db.execute('DELETE FROM jobs WHERE job_id=?',(jid,))
                for table in ('versions','acl','projection'):
                    self.db.execute(f'DELETE FROM {table} WHERE tenant=? AND doc_id=?',scope)
                self.db.execute('UPDATE documents SET purge_at=NULL WHERE tenant=? AND doc_id=?',scope)
        return len(scopes)
