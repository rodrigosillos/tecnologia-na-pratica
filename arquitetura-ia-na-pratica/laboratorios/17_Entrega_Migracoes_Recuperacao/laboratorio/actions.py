"""Chapter 15: durable local intent and a separate, simulated task destination.

No network, real identity service, model, background dispatcher, or production
security boundary. Administrative fixture methods and Python callers are trusted.
"""
from contextlib import contextmanager
from hashlib import sha256
from uuid import uuid4
import copy,json,sqlite3
from base.store import Actor
from control import Session,run,unique_object
from routing import sources_valid

POLICY='task-approval-v1'
FINAL={'succeeded','rejected','cancelled','expired','invalidated'}


class Denied(ValueError):pass
class Rejected(Exception):pass
class ProcessCrash(BaseException):pass


def canonical(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,
                      separators=(',',':'),allow_nan=False)


def digest(value):
    return sha256(canonical(value).encode('utf-8')).hexdigest()


def parse_draft(raw):
    if type(raw) is not str or len(raw.encode('utf-8'))>512:
        raise Denied('schema')
    try:obj=json.loads(raw,object_pairs_hook=unique_object)
    except (ValueError,RecursionError):raise Denied('schema') from None
    if type(obj) is not dict or set(obj)!={'tool','project','topic'}:
        raise Denied('schema')
    if any(type(v) is not str for v in obj.values()):
        raise Denied('schema')
    if obj['tool']!='prepare_task' or obj['project']!='ops':
        raise Denied('scope')
    if obj['topic'] not in ('returns','shipping'):
        raise Denied('scope')
    return obj


def prepare(store,actor,raw,language='pt-BR'):
    draft=parse_draft(raw)
    session=Session(store,actor,language)
    result=run(session)
    if result['state']!='complete':raise Denied('evidence')
    row=next(r for r in result['output']['rows']
             if r['topic']==draft['topic'])
    if row['same']:raise Denied('no_change')
    saved=[session.saved[session.by_doc[d]] for d in session.documents]
    payload={'operation':'create-review-task-v1',
        'tenant':actor.tenant,'requester':actor.user,
        'project':'ops','language':language,
        'topic':row['topic'],'left_days':row['left'],
        'right_days':row['right'],'delta_days':row['delta'],
        'sources':result['output']['sources']}
    return {'policy':POLICY,'payload':payload,'evidence':saved}


def display(payload):
    pt=payload['language']=='pt-BR'
    title='Revisar divergência de devolução' if pt else 'Review returns discrepancy'
    facts=f"{payload['left_days']} -> {payload['right_days']}"
    body=(f"Prazo: {facts} dias; diferença {payload['delta_days']} dias."
          if pt else f"Window: {facts} days; delta {payload['delta_days']} days.")
    return {'title':title,'body':body,'project':payload['project'],
            'operation':payload['operation'],'sources':payload['sources']}


@contextmanager
def transaction(db):
    db.execute('BEGIN IMMEDIATE')
    try:
        yield
        db.execute('COMMIT')
    except BaseException:
        db.execute('ROLLBACK');raise


def connect(path):
    db=sqlite3.connect(str(path),isolation_level=None)
    db.row_factory=sqlite3.Row
    return db


class TaskDestination:
    """Separate SQLite DB; permanent key retention in this teaching fixture."""
    def __init__(self,path=':memory:'):
        self.db=connect(path);self.calls=0;self.lookups=0
        self.db.execute('CREATE TABLE IF NOT EXISTS tasks ('
            'tenant TEXT,key TEXT,hash TEXT,payload TEXT,receipt TEXT,'
            'PRIMARY KEY(tenant,key))')
    def close(self):self.db.close()
    def count(self):return self.db.execute('SELECT COUNT(*) FROM tasks').fetchone()[0]
    def lookup(self,tenant,key,expected):
        self.lookups+=1
        row=self.db.execute('SELECT * FROM tasks WHERE tenant=? AND key=?',(tenant,key)).fetchone()
        if row and row['hash']!=expected:raise Denied('key_conflict')
        return row['receipt'] if row else None
    def create(self,tenant,key,payload,fault=None):
        if fault not in (None,'before','after','reject'):raise ValueError('fault')
        self.calls+=1
        if fault=='before':raise TimeoutError('simulated transport')
        if fault=='reject':raise Rejected('definite refusal before effect')
        expected=digest(payload)
        with transaction(self.db):
            row=self.db.execute('SELECT * FROM tasks WHERE tenant=? AND key=?',(tenant,key)).fetchone()
            if row:
                if row['hash']!=expected:raise Denied('key_conflict')
                receipt=row['receipt']
            else:
                receipt='task-'+str(self.count()+1).zfill(4)
                self.db.execute('INSERT INTO tasks VALUES (?,?,?,?,?)',
                    (tenant,key,expected,canonical(payload),receipt))
        if fault=='after':raise TimeoutError('reply lost after commit')
        return receipt


class ActionService:
    def __init__(self,store,path=':memory:'):
        self.store=store;self.db=connect(path)
        self.db.executescript('''
        CREATE TABLE IF NOT EXISTS grants (
          tenant TEXT,subject TEXT,role TEXT,active INTEGER,
          PRIMARY KEY(tenant,subject));
        CREATE TABLE IF NOT EXISTS intents (
          id TEXT PRIMARY KEY,tenant TEXT,requester TEXT,packet TEXT,hash TEXT,
          created INTEGER,expires INTEGER,state TEXT,reviewer TEXT,
          approved_hash TEXT,approved_at INTEGER,attempts INTEGER DEFAULT 0,
          receipt TEXT,reason TEXT);
        CREATE TABLE IF NOT EXISTS audit (
          seq INTEGER PRIMARY KEY AUTOINCREMENT,id TEXT,event TEXT,
          subject TEXT,at INTEGER,hash TEXT);
        ''')
    def close(self):self.db.close()
    def grant(self,actor,role,active=True):
        if role not in ('requester','reviewer'):raise ValueError('role')
        self.db.execute('INSERT INTO grants VALUES (?,?,?,?) ON CONFLICT(tenant,subject) '
            'DO UPDATE SET role=excluded.role,active=excluded.active',
            (actor.tenant,actor.user,role,int(active)))
    def allowed(self,actor,role):
        row=self.db.execute('SELECT role,active FROM grants WHERE tenant=? AND subject=?',
            (actor.tenant,actor.user)).fetchone()
        return bool(row and row['active'] and row['role']==role)
    def row(self,id):
        row=self.db.execute('SELECT * FROM intents WHERE id=?',(id,)).fetchone()
        if not row:raise Denied('not_found')
        return dict(row)
    def log(self,row,event,subject,now):
        self.db.execute('INSERT INTO audit(id,event,subject,at,hash) VALUES (?,?,?,?,?)',
            (row['id'],event,subject,now,row['hash']))
    def transition(self,row,state,reason,now,subject='worker'):
        self.db.execute('UPDATE intents SET state=?,reason=? WHERE id=?',(state,reason,row['id']))
        self.log(row,state,subject,now)
    def check_time(self,row,now):
        lower=max(row['created'],row.get('approved_at') or row['created'])
        if type(now) is not int or now<lower:raise Denied('clock')
    def failure(self,row,now,approved=False):
        self.check_time(row,now)
        packet=json.loads(row['packet'])
        if digest(packet)!=row['hash'] or packet['policy']!=POLICY:return 'integrity'
        if now>=row['expires']:return 'expired'
        actor=Actor(row['tenant'],row['requester'])
        if not self.allowed(actor,'requester'):return 'requester_revoked'
        if not sources_valid(self.store,actor,packet['evidence'],packet['payload']['language']):return 'stale'
        if approved:
            reviewer=Actor(row['tenant'],row['reviewer'])
            if row['approved_hash']!=row['hash']:return 'approval_mismatch'
            if reviewer.user==actor.user or not self.allowed(reviewer,'reviewer'):return 'reviewer_revoked'
        return None
    def propose(self,actor,raw,now=0,ttl=30,language='pt-BR'):
        if type(now) is not int or now<0 or type(ttl) is not int or not 1<=ttl<=3600:raise Denied('clock')
        if not self.allowed(actor,'requester'):raise Denied('requester')
        packet=prepare(self.store,actor,raw,language);id=uuid4().hex
        with transaction(self.db):
            if not self.allowed(actor,'requester'):raise Denied('requester')
            self.db.execute('INSERT INTO intents(id,tenant,requester,packet,hash,created,expires,state) '
                'VALUES (?,?,?,?,?,?,?,?)',(id,actor.tenant,actor.user,canonical(packet),digest(packet),now,now+ttl,'pending'))
            self.log(self.row(id),'pending',actor.user,now)
        return id
    def preview(self,actor,id):
        row=self.row(id)
        own=actor.user==row['requester'] and self.allowed(actor,'requester')
        if actor.tenant!=row['tenant'] or not (own or self.allowed(actor,'reviewer')):raise Denied('viewer')
        packet=json.loads(row['packet'])
        if digest(packet)!=row['hash']:raise Denied('integrity')
        # Current source access is checked for the requester, not delegated to the reviewer.
        if not sources_valid(self.store,Actor(row['tenant'],row['requester']),packet['evidence'],packet['payload']['language']):
            raise Denied('stale')
        return {'id':id,'hash':row['hash'],'state':row['state'],
                'expires':row['expires'],'action':display(packet['payload'])}
    def decide(self,reviewer,id,expected,accept,now=1):
        if type(accept) is not bool:raise Denied('decision')
        with transaction(self.db):
            row=self.row(id);self.check_time(row,now)
            if reviewer.tenant!=row['tenant'] or reviewer.user==row['requester'] or not self.allowed(reviewer,'reviewer'):
                raise Denied('reviewer')
            if row['state']!='pending':raise Denied('state')
            if expected!=row['hash']:raise Denied('preview_mismatch')
            reason=self.failure(row,now)
            if reason:raise Denied(reason)
            if not accept:self.transition(row,'rejected','human',now,reviewer.user)
            else:
                self.db.execute('UPDATE intents SET reviewer=?,approved_hash=?,approved_at=? WHERE id=?',
                    (reviewer.user,expected,now,id))
                self.transition(row,'approved','human',now,reviewer.user)
        return self.row(id)['state']
    def cancel(self,actor,id,now=2):
        with transaction(self.db):
            row=self.row(id);self.check_time(row,now)
            if (actor.tenant,actor.user)!=(row['tenant'],row['requester']):raise Denied('requester')
            if row['state'] not in ('pending','approved'):raise Denied('too_late')
            self.transition(row,'cancelled','user',now,actor.user)
        return 'cancelled'
    def claim(self,id,now,retry=False):
        with transaction(self.db):
            row=self.row(id)
            if row['state']!=('unknown' if retry else 'approved'):return None
            reason=self.failure(row,now,approved=True)
            if reason:
                if not retry:self.transition(row,'expired' if reason=='expired' else 'invalidated',reason,now)
                else:
                    self.db.execute('UPDATE intents SET reason=? WHERE id=?',(reason,id))
                    self.log(row,'retry_blocked','worker',now)
                return None
            if row['attempts']>=2:
                self.db.execute('UPDATE intents SET reason=? WHERE id=?',('attempt_limit',id))
                return None
            self.db.execute('UPDATE intents SET attempts=attempts+1 WHERE id=?',(id,))
            self.transition(row,'dispatching','claimed',now)
        return self.row(id)
    def dispatch(self,id,destination,now=2,fault=None,crash=None,retry=False):
        if crash not in (None,'before','after'):raise ValueError('crash')
        row=self.claim(id,now,retry)
        if row is None:return self.row(id)['state']
        if crash=='before':raise ProcessCrash('after claim, before destination')
        payload=json.loads(row['packet'])['payload']
        try:receipt=destination.create(row['tenant'],row['id'],payload,fault)
        except Rejected:
            with transaction(self.db):self.transition(row,'rejected','destination',now)
            return 'rejected'
        except Exception:
            # Transport and unclassified adapter errors are ambiguous, not proof of no effect.
            with transaction(self.db):self.transition(row,'unknown','ambiguous',now)
            return 'unknown'
        if crash=='after':raise ProcessCrash('destination committed; local success missing')
        with transaction(self.db):
            self.db.execute('UPDATE intents SET receipt=? WHERE id=?',(receipt,id))
            self.transition(row,'succeeded','receipt',now)
        return 'succeeded'
    def recover(self,id,now=3):
        # Administrative operation only after proving the old dispatcher is dead.
        with transaction(self.db):
            row=self.row(id);self.check_time(row,now)
            if row['state']=='dispatching':self.transition(row,'unknown','recovered',now)
        return self.row(id)['state']
    def reconcile(self,id,destination,now=3,retry=False):
        row=self.row(id);self.check_time(row,now)
        if row['state']!='unknown':return row['state']
        packet=json.loads(row['packet'])
        if digest(packet)!=row['hash']:raise Denied('integrity')
        try:receipt=destination.lookup(row['tenant'],id,digest(packet['payload']))
        except Exception:return 'unknown'
        if receipt:
            with transaction(self.db):
                self.db.execute('UPDATE intents SET receipt=? WHERE id=?',(receipt,id))
                self.transition(row,'succeeded','reconciled',now)
            return 'succeeded'
        if retry:return self.dispatch(id,destination,now,retry=True)
        return 'unknown'
    def events(self,id):
        return [dict(r) for r in self.db.execute('SELECT event,subject,at FROM audit WHERE id=? ORDER BY seq',(id,))]
