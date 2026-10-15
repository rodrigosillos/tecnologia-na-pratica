"""Chapter 18: local integrated drill, synthetic provider, no network."""
from pathlib import Path
import json
from async_jobs import (Jobs,LocalQueue,TERMINAL,IdempotencyConflict,
    canonical_payload,request_fingerprint,transaction,LeaseLost)
from job_worker import manuals,payload,capture,compare,still_valid,read_job
from resilience import (Clock,Controller,Policy,CircuitBreaker,RetryBudget,
    ScriptedProvider,Step,integer)
from security_gate import Boundary,Scope,fact_candidate
from actions import Denied
from fixtures import ALICE


class AdmissionClosed(ValueError):pass


def admission_reason(paused,pending,capacity):
    if paused:return 'paused'
    if pending>=capacity:return 'capacity'
    return None


class BoundedJobs(Jobs):
    """Global unfinished-job cap, persisted alongside jobs. Not broker capacity."""
    def __init__(self,path=':memory:',capacity=2):
        integer(capacity,'capacity',1)
        super().__init__(path)
        self.db.execute('''CREATE TABLE IF NOT EXISTS admission(
            id INTEGER PRIMARY KEY,capacity INTEGER NOT NULL,paused INTEGER NOT NULL)''')
        self.db.execute('INSERT OR IGNORE INTO admission VALUES(1,?,0)',(capacity,))
    def pause(self,value=True):
        if type(value) is not bool:raise ValueError('pause')
        with transaction(self.db):
            self.db.execute('UPDATE admission SET paused=? WHERE id=1',(int(value),))
    def pending(self):
        return self.db.execute("SELECT count(*) FROM jobs WHERE state IN ('queued','running','retry_wait')").fetchone()[0]
    def submit(self,actor,key,spec,now,validity_ms=1800):
        integer(now,'now');integer(validity_ms,'validity_ms',1)
        if type(key) is not str or not 1<=len(key)<=100:raise ValueError('key')
        raw=canonical_payload(spec);fingerprint=request_fingerprint(spec)
        self.expire(now)
        with transaction(self.db):
            old=self.db.execute('''SELECT id,fingerprint FROM jobs WHERE
                tenant=? AND subject=? AND operation=? AND idem_key=?''',
                (actor.tenant,actor.user,'compare-manuals-v1',key)).fetchone()
            if old:
                if old['fingerprint']!=fingerprint:raise IdempotencyConflict('intent')
                return {'job_id':old['id'],'replay':True}
            limit=self.db.execute('SELECT * FROM admission WHERE id=1').fetchone()
            reason=admission_reason(limit['paused'],self.pending(),limit['capacity'])
            if reason:raise AdmissionClosed(reason)
            cur=self.db.execute('''INSERT INTO jobs
                (tenant,subject,operation,idem_key,fingerprint,payload,
                 state,created_ms,deadline_ms,next_ms)
                VALUES(?,?,?,?,?,?,'queued',?,?,?)''',
                (actor.tenant,actor.user,'compare-manuals-v1',key,
                 fingerprint,raw,now,now+validity_ms,now))
            jid=cur.lastrowid
            self.db.execute('INSERT INTO dispatch_outbox(job_id) VALUES(?)',(jid,))
        return {'job_id':jid,'replay':False}
    def stop(self,lease,now,reason):
        with transaction(self.db):
            self._guard(lease,now)
            self._terminal(lease.job_id,'failed',reason)


def release_decision(evidence):
    required={'containment','capacity','recovery',
              'live_quality','operations'}
    if set(evidence)!=required:raise ValueError('evidence set')
    for item in evidence.values():
        if set(item)!={'status','reference'}:raise ValueError('fields')
        if item['status'] not in ('pass','fail','unmeasured'):
            raise ValueError('status')
        if type(item['reference']) is not str:
            raise ValueError('reference')
        if item['status']!='unmeasured' and not item['reference'].strip():
            raise ValueError('evidence reference required')
    failed=sorted(k for k,v in evidence.items()
                  if v['status']=='fail')
    missing=sorted(k for k,v in evidence.items()
                   if v['status']=='unmeasured')
    decision='hold' if failed or missing else 'review_candidate'
    return {'decision':decision,
            'failed':failed,'unmeasured':missing}


class Drill:
    def __init__(self,language='pt-BR',capacity=2,path=None):
        if language not in ('pt-BR','en-US'):raise ValueError('language')
        self.language=language;self.path=Path(path) if path else None
        self.jobs=BoundedJobs(self.path/'jobs.db' if path else ':memory:',capacity)
        self.queue=LocalQueue(self.path/'queue.db' if path else ':memory:')
        self.store=manuals();self.clock=Clock();self.breaker=CircuitBreaker(2,100)
        self.retries=RetryBudget(2);self.provider_mode='healthy';self.candidate='fact'
        self.events=[];self.admitted=[];self.rejected=0;self.replays=0
        self.calls=0;self.peak=0;self.before_complete=None
    def close(self):
        self.jobs.close();self.queue.close();self.store.close()
    def emit(self,stage,reason,jid=None):
        self.events.append({'at_ms':self.clock.now,'stage':stage,
                            'reason':reason,'job':jid})
    def submit(self,key,validity_ms=1800,actor=ALICE,spec=None):
        try:
            answer=self.jobs.submit(actor,key,spec or payload(self.language),
                                    self.clock.now,validity_ms)
        except AdmissionClosed as e:
            self.rejected+=1;self.emit('admission',str(e));return None
        jid=answer['job_id']
        if answer['replay']:self.replays+=1
        else:self.admitted.append(jid)
        self.emit('admission','replay' if answer['replay'] else 'accepted',jid)
        self.peak=max(self.peak,self.jobs.pending());return jid
    def reopen(self):
        if self.path is None:raise ValueError('file storage required')
        self.jobs.close();self.queue.close()
        self.jobs=BoundedJobs(self.path/'jobs.db')
        self.queue=LocalQueue(self.path/'queue.db')
        # Deliberately keep clock, breaker, source fixture and audit in memory.
    def step(self):
        self.jobs.relay(self.queue,self.clock.now)
        receipt=self.queue.receive(self.clock.now,visibility_ms=300)
        if receipt is None:return 'empty'
        lease=self.jobs.claim(receipt.job_id,'drill',self.clock.now,
                              lease_ms=300,max_attempts=2)
        if lease is None:
            row=self.jobs.job(receipt.job_id)
            if row is None or row['state'] in TERMINAL:
                self.queue.ack(receipt,self.clock.now);return 'terminal'
            return 'deferred'
        row=self.jobs.job(lease.job_id);spec=json.loads(row['payload'])
        from base.store import Actor
        actor=Actor(row['tenant'],row['subject'])
        try:
            gates=[Boundary(self.store,Scope(actor,document=doc,topic=topic,
                     language=spec['language']))
                   for doc in spec['documents'] for topic in ('returns','shipping')]
            for gate in gates:gate.context()
        except Denied:
            return self.block(lease,receipt,'source_access')
        available=row['deadline_ms']-self.clock.now-20
        if available<40:return self.block(lease,receipt,'insufficient_time')
        policy=Policy(budget_ms=min(250,available),attempt_ms=60,
                      reserve_ms=30,minimum_ms=10,max_attempts=2,base_ms=10,cap_ms=20)
        provider=ScriptedProvider([Step(10,'503' if self.provider_mode=='down' else 'ok')]*2)
        result=Controller(self.clock,policy,self.breaker,self.retries).run(provider)
        self.calls+=provider.calls;self.emit('provider',result['reason'],lease.job_id)
        if result['reason']!='success':
            self.jobs.fail(lease,self.clock.now,delay_ms=200,max_attempts=2)
            return 'retry_or_failed'
        for gate in gates:
            raw=fact_candidate(gate)
            if self.candidate=='egress':raw='{"kind":"fetch","url":"https://sink.invalid/"}'
            if self.candidate=='approval':raw='{"kind":"propose","topic":"returns","approved":true}'
            accepted=gate.accept(raw)
            if accepted['status']!='answered':
                return self.block(lease,receipt,'security:'+accepted['reason'])
        try:
            for position in range(row['stage'],2):
                value=capture(self.store,actor,spec['documents'][position],spec['language'])
                self.clock.advance(10)
                self.jobs.checkpoint(lease,position,value,self.clock.now)
            if self.before_complete:self.before_complete(self)
            saved=self.jobs.saved(lease.job_id)
            if not all(still_valid(self.store,actor,v,spec['language']) for v in saved):
                return self.block(lease,receipt,'source_changed')
            self.jobs.complete(lease,compare(saved),self.clock.now)
            self.queue.ack(receipt,self.clock.now);self.emit('result','succeeded',lease.job_id)
            return 'succeeded'
        except ValueError:return self.block(lease,receipt,'source_format')
        except LeaseLost:
            self.jobs.expire(self.clock.now);self.emit('result','lease_lost',lease.job_id)
            return 'lease_lost'
    def block(self,lease,receipt,reason):
        self.jobs.stop(lease,self.clock.now,reason)
        self.queue.ack(receipt,self.clock.now);self.emit('result',reason,lease.job_id)
        return 'blocked'
    def drain(self,max_steps=20):
        for _ in range(max_steps):
            self.step()
            if self.jobs.pending()==0 and self.queue.pending()==0:return
            self.clock.advance(300)
        raise RuntimeError('drill did not settle')
    def report(self):
        states={r['state']:r['n'] for r in self.jobs.db.execute('SELECT state,count(*) n FROM jobs GROUP BY state')}
        public=[read_job(self.jobs,self.store,ALICE,jid,self.clock.now) for jid in self.admitted]
        visible=[p['result'] for p in public if p and p['result'] is not None]
        return {'admitted':len(self.admitted),'rejected':self.rejected,'replays':self.replays,
            'peak_pending':self.peak,'states':states,'result_rows':self.jobs.db.execute('SELECT count(*) FROM job_results').fetchone()[0],
            'visible_results':len(visible),'return_deltas':[v['rows'][0]['delta'] for v in visible],
            'provider_calls':self.calls,'virtual_ms':self.clock.now,'circuit':self.breaker.state,
            'pending_messages':self.queue.pending(),'events':list(self.events)}
