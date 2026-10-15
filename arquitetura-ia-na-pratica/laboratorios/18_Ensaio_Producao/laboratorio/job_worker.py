"""Compare two fictional manuals; extraction is deterministic, not an LLM."""
from dataclasses import asdict
import json
import re
from base.store import Actor
from fixtures import seeded, ingest
from retrieval import PATTERNS
from async_jobs import TERMINAL, Crash, LeaseLost


def manuals():
    store=seeded()
    ingest(store,'manual-a',
        'Devolução: prazo de 45 dias. Postagem: despacho em 3 dias.',
        'Returns: window of 45 days. Shipping: dispatch in 3 days.')
    ingest(store,'manual-b',
        'Devolução: prazo de 30 dias. Postagem: despacho em 3 dias.',
        'Returns: window of 30 days. Shipping: dispatch in 3 days.')
    return store


def payload(language='pt-BR'):
    return dict(language=language,documents=['manual-a','manual-b'])


def capture(store, actor, document, language):
    snapshot=store.prepare(actor,document,language)
    if snapshot is None: raise ValueError('source not available')
    facts={}
    for topic in ('returns','shipping'):
        matches=list(re.finditer(PATTERNS[language][topic],snapshot.body))
        if len(matches)!=1: raise ValueError('unsupported manual format')
        facts[topic]=dict(value=int(matches[0].group(1)),quote=matches[0].group(0))
    metadata=asdict(snapshot);metadata.pop('body')
    return dict(snapshot=metadata,facts=facts)


def still_valid(store, actor, saved, language):
    try:
        return capture(store,actor,saved['snapshot']['document'],language)==saved
    except ValueError:
        return False


def compare(saved):
    if len(saved)!=2:raise ValueError('two captures required')
    rows=[]
    for topic in ('returns','shipping'):
        left=saved[0]['facts'][topic]['value']
        right=saved[1]['facts'][topic]['value']
        rows.append(dict(topic=topic,left=left,right=right,
                         delta=right-left,same=left==right,unit='days'))
    return dict(schema_version='1.0',
                operation='compare-manuals-v1',rows=rows)


def work_once(jobs, queue, store, clock, worker='worker-a',
              crash_at=None, transient=False, before_complete=None):
    receipt=queue.receive(clock.now)
    if receipt is None:return 'empty'
    lease=jobs.claim(receipt.job_id,worker,clock.now)
    if lease is None:
        row=jobs.job(receipt.job_id)
        if row is None or row['state'] in TERMINAL:
            queue.ack(receipt,clock.now);return 'terminal_delivery'
        return 'deferred'
    if transient:
        jobs.fail(lease,clock.now);return 'retry_scheduled'
    row=jobs.job(lease.job_id);spec=json.loads(row['payload'])
    actor=Actor(row['tenant'],row['subject'])
    try:
        for position in range(row['stage'],2):
            value=capture(store,actor,spec['documents'][position],spec['language'])
            clock.advance(10)
            jobs.checkpoint(lease,position,value,clock.now)
            if crash_at=='checkpoint' and position==0:
                raise Crash('worker stopped after checkpoint commit')
        saved=jobs.saved(lease.job_id)
        if before_complete:before_complete()
        if not all(still_valid(store,actor,v,spec['language']) for v in saved):
            jobs.fail(lease,clock.now,transient=False)
        else:
            jobs.complete(lease,compare(saved),clock.now)
        if crash_at=='result':raise Crash('worker stopped after result commit')
        queue.ack(receipt,clock.now)
        return jobs.job(lease.job_id)['state']
    except ValueError:
        jobs.fail(lease,clock.now,transient=False)
        queue.ack(receipt,clock.now);return 'failed'
    except LeaseLost:
        jobs.expire(clock.now)
        return 'lease_lost'


def read_job(jobs, store, actor, job_id, now):
    jobs.expire(now)
    row=jobs.job(job_id)
    if not row or (row['tenant'],row['subject'])!=(actor.tenant,actor.user):
        return None
    public=dict(job_id=job_id,state=row['state'],
                completed_steps=row['stage'],total_steps=2,result=None)
    if row['state']=='succeeded':
        spec=json.loads(row['payload']);saved=jobs.saved(job_id)
        # One consistent source snapshot for the authorization/read boundary.
        store.db.execute('BEGIN')
        try:
            valid=all(still_valid(store,actor,v,spec['language']) for v in saved)
        finally:
            store.db.execute('COMMIT')
        if not valid:
            public['result_access']='unavailable';return public
        result=json.loads(jobs.db.execute('SELECT value FROM job_results WHERE job_id=?',
                                         (job_id,)).fetchone()[0])
        result['sources']=[dict(document=v['snapshot']['document'],
            version=v['snapshot']['version'],source=v['snapshot']['source'],
            quotes=[f['quote'] for f in v['facts'].values()]) for v in saved]
        public['result']=result;public['result_access']='available'
    return public
