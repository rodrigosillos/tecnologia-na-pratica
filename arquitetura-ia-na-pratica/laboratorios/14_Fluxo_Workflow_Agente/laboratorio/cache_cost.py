"""Chapter 12: offline, synthetic units; no provider billing or network."""
from contextlib import contextmanager
from dataclasses import asdict
import hashlib
import json
import sqlite3
from threading import Lock
from job_worker import capture, compare
from routing import (route, RoutePolicy, registry, approvals, sources_valid,
                     validate_rows, TOPICS)

OVERHEAD=4  # lookup 1 + source checks 2 + result validation 1, fictional


def canonical(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,
                      separators=(',',':'))


def answer_key(actor, saved, language, config):
    envelope={'tenant':actor.tenant,'user':actor.user,
              'language':language,'operation':'compare-manuals-v1',
              'sources':[s['snapshot'] for s in saved],
              'config':config}
    return hashlib.sha256(canonical(envelope).encode()).hexdigest()


def reusable(result):
    # Request costs, traces, timing and attempt counts are never cached.
    return {k:result[k] for k in ('rows','sources','model')}


def cached_valid(payload, saved):
    if type(payload) is not dict:return False
    if set(payload)!={'rows','sources','model'}:return False
    if type(payload['model']) is not str:return False
    gold=compare(saved)['rows']
    packet={'schema_version':'1.0','rows':payload['rows']}
    if validate_rows(packet,gold)!=gold:return False
    expected=[dict(document=s['snapshot']['document'],
                   version=s['snapshot']['version'],
                   source=s['snapshot']['source'],
                   quotes=[s['facts'][t]['quote'] for t in TOPICS])
              for s in saved]
    return payload['sources']==expected


def integer(value, minimum=0):
    if type(value) is not int or value<minimum:raise ValueError('integer')
    return value


@contextmanager
def transaction(db):
    db.execute('BEGIN IMMEDIATE')
    try:
        yield
        db.execute('COMMIT')
    except BaseException:
        db.execute('ROLLBACK')
        raise


class AnswerCache:
    def __init__(self,path=':memory:',max_entries=64,max_bytes=16384):
        self.limit=integer(max_entries,1);self.max_bytes=integer(max_bytes,1)
        self.db=sqlite3.connect(path,isolation_level=None,timeout=5)
        self.db.execute('''CREATE TABLE IF NOT EXISTS answers(
            key TEXT PRIMARY KEY, body TEXT NOT NULL,
            created INTEGER NOT NULL, expires INTEGER NOT NULL)''')

    def close(self):self.db.close()

    def get(self,key,now):
        integer(now)
        row=self.db.execute('SELECT body,expires FROM answers WHERE key=?',
                            (key,)).fetchone()
        if row is None or now>=row[1]:return None
        try:return json.loads(row[0])
        except (ValueError,TypeError):return None

    def put(self,key,payload,now,ttl):
        integer(now);integer(ttl,1)
        body=canonical(payload)
        if len(body.encode())>self.max_bytes:return False
        with transaction(self.db):
            self.db.execute('DELETE FROM answers WHERE expires<=?',(now,))
            self.db.execute('INSERT OR REPLACE INTO answers VALUES(?,?,?,?)',
                            (key,body,now,now+ttl))
            excess=self.db.execute('SELECT count(*) FROM answers').fetchone()[0]-self.limit
            if excess>0:
                self.db.execute('''DELETE FROM answers WHERE key IN
                    (SELECT key FROM answers ORDER BY created,key LIMIT ?)''',
                    (excess,))
        return True


class Ledger:
    def __init__(self,path=':memory:'):
        self.db=sqlite3.connect(path,isolation_level=None,timeout=5)
        self.db.row_factory=sqlite3.Row
        self.db.executescript('''
            CREATE TABLE IF NOT EXISTS limits(
              tenant TEXT PRIMARY KEY, cap INTEGER NOT NULL);
            CREATE TABLE IF NOT EXISTS tasks(
              tenant TEXT NOT NULL, task TEXT NOT NULL, fingerprint TEXT NOT NULL,
              reserved INTEGER NOT NULL, state TEXT NOT NULL, actual INTEGER,
              PRIMARY KEY(tenant,task));
        ''')

    def close(self):self.db.close()

    def configure(self,tenant,cap):
        integer(cap)
        with transaction(self.db):
            row=self.db.execute('SELECT cap FROM limits WHERE tenant=?',(tenant,)).fetchone()
            if row and row['cap']!=cap:raise ValueError('existing cap differs')
            self.db.execute('INSERT OR IGNORE INTO limits VALUES(?,?)',(tenant,cap))

    def balance(self,tenant):
        # One SQL statement: a consistent view even with other connections.
        row=self.db.execute('''SELECT cap,
            COALESCE(SUM(CASE WHEN state='settled' THEN actual ELSE 0 END),0) spent,
            COALESCE(SUM(CASE WHEN state!='settled' THEN reserved ELSE 0 END),0) held
            FROM limits LEFT JOIN tasks USING(tenant)
            WHERE limits.tenant=? GROUP BY limits.tenant''',(tenant,)).fetchone()
        if row is None:raise ValueError('unknown tenant')
        result=dict(row);result['available']=result['cap']-result['spent']-result['held']
        return result

    def reserve(self,tenant,task,fingerprint,maximum):
        integer(maximum,1)
        if not task or not fingerprint:raise ValueError('identity')
        with transaction(self.db):
            old=self.db.execute('SELECT * FROM tasks WHERE tenant=? AND task=?',
                                (tenant,task)).fetchone()
            if old:return 'duplicate' if old['fingerprint']==fingerprint else 'conflict'
            if self.balance(tenant)['available']<maximum:return 'budget'
            self.db.execute('INSERT INTO tasks VALUES(?,?,?,?,?,NULL)',
                            (tenant,task,fingerprint,maximum,'pending'))
            return 'admitted'

    def uncertain(self,tenant,task):
        with transaction(self.db):
            row=self._task(tenant,task)
            if row['state']=='settled':raise ValueError('already settled')
            self.db.execute("UPDATE tasks SET state='unknown' WHERE tenant=? AND task=?",
                            (tenant,task))

    def settle(self,tenant,task,actual):
        integer(actual)
        with transaction(self.db):
            row=self._task(tenant,task)
            if actual>row['reserved']:raise ValueError('exceeds reservation')
            if row['state']=='settled':
                if row['actual']!=actual:raise ValueError('conflicting settlement')
                return
            self.db.execute("UPDATE tasks SET state='settled',actual=? WHERE tenant=? AND task=?",
                            (actual,tenant,task))

    def _task(self,tenant,task):
        row=self.db.execute('SELECT * FROM tasks WHERE tenant=? AND task=?',
                            (tenant,task)).fetchone()
        if row is None:raise ValueError('unknown task')
        return dict(row)


class Gate:
    """Process-local admission and single flight, held until work actually exits."""
    def __init__(self,limit=2):
        self.limit=integer(limit,1);self.lock=Lock();self.active=set()

    def enter(self,key):
        with self.lock:
            if key in self.active:return 'in_flight'
            if len(self.active)>=self.limit:return 'capacity'
            self.active.add(key);return 'admitted'

    def leave(self,key):
        with self.lock:self.active.remove(key)


def snapshot(store,actor,documents,language):
    store.db.execute('BEGIN')
    try:return [capture(store,actor,d,language) for d in documents]
    finally:store.db.execute('COMMIT')


def execute(store,actor,cache,ledger,gate,task,language='pt-BR',
            documents=('manual-a','manual-b'),policy=None,adapter=None,
            now=0,ttl=1000,prompt='compare-v1',after_lookup=None,
            use_cache=True):
    integer(now);integer(ttl,1)
    if language not in ('pt-BR','en-US'):raise ValueError('language')
    if len(documents)!=2 or len(set(documents))!=2:raise ValueError('documents')
    policy=policy or RoutePolicy()
    config={'prompt':prompt,'schema':'1.0','router':'route-v1',
            'policy':asdict(policy),'registry':[asdict(m) for m in registry()],
            'approved':sorted(approvals(registry()))}
    def result(state,reason,hit=False,calls=0,units=0,held=0,payload=None):
        return dict(state=state,reason=reason,cache_hit=hit,model_calls=calls,
                    task_units=units,held_units=held,payload=payload)
    try:saved=snapshot(store,actor,documents,language)
    except ValueError:return result('abstain','access')
    key=answer_key(actor,saved,language,config)
    payload=cache.get(key,now) if use_cache else None
    hit=payload is not None and cached_valid(payload,saved)
    if after_lookup:after_lookup()
    if not sources_valid(store,actor,saved,language):
        return result('abstain','source_changed')
    admission=gate.enter(key)
    if admission!='admitted':return result('deferred',admission)
    try:
        maximum=OVERHEAD if hit else OVERHEAD+policy.max_units
        admission=ledger.reserve(actor.tenant,task,key,maximum)
        if admission!='admitted':return result('deferred',admission)
        if hit:
            ledger.settle(actor.tenant,task,OVERHEAD)
            # Last read authorization point, not revocation of sent bytes.
            if not sources_valid(store,actor,saved,language):
                return result('abstain','source_changed',units=OVERHEAD)
            return result('full','cache',True,units=OVERHEAD,payload=payload)
        try:
            routed=route(store,actor,language,documents,policy=policy,adapter=adapter)
        except Exception:
            ledger.uncertain(actor.tenant,task)
            return result('abstain','cost_unknown',held=maximum)
        actual=OVERHEAD+routed['charged_units']
        ledger.settle(actor.tenant,task,actual)
        valid=sources_valid(store,actor,saved,language)
        if not valid:return result('abstain','source_changed',calls=routed['calls'],units=actual)
        payload=reusable(routed) if routed['rows'] else None
        if use_cache and routed['state']=='full' and cached_valid(payload,saved):
            cache.put(key,payload,now,ttl)
        return result(routed['state'],routed['reason'],calls=routed['calls'],
                      units=actual,payload=payload)
    finally:gate.leave(key)
