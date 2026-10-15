from pathlib import Path
import json
from pipeline import Pipeline, Actor, Copilot, Conflict, LostLease

ALICE = Actor('acme', 'alice')
BOB = Actor('zen', 'bob')
SOURCE = {
    'pt-BR': 'Prazo: 45 dias. A devolução exige o comprovante da compra. '
             'O produto deve manter os acessórios originais. Solicite a '
             'etiqueta de postagem no portal. A aprovação depende da conferência.',
    'en-US': 'Window: 45 days. Returns require proof of purchase. '
             'The product must include its original accessories. Request '
             'a shipping label in the portal. Approval depends on inspection.'}

def raw_source():
    return json.dumps(SOURCE, ensure_ascii=False).encode('utf-8')

def seeded(path=':memory:'):
    s = Pipeline(path)
    s.principal('acme', 'alice', 'staff')
    s.principal('acme', 'ana', 'admin')
    s.principal('zen', 'bob', 'staff')
    s.publish('acme', 'returns', 'Prazo: 30 dias.', 'Window: 30 days.',
              'urn:acme:returns:v1', ['staff', 'admin'], 0, 'a-1')
    s.publish('zen', 'returns', 'Prazo: 7 dias.', 'Window: 7 days.',
              'urn:zen:returns:v1', ['staff'], 0, 'z-1')
    s.drain()
    return s

def submit(s, **changes):
    args = dict(tenant='acme', doc='returns', raw=raw_source(),
                source='urn:acme:returns:v2', roles=['staff','admin'],
                expected=1, request_id='import-2')
    args.update(changes)
    return s.submit(**args)

def stage(s, lease, now):
    s.prepare_job(lease, now)
    while s.job(lease.job)['state'] == 'staging':
        s.write_batch(lease, now)

def run_scenarios():
    rows=[]
    def record(name, ok, observed):
        rows.append(dict(scenario=name, passed=bool(ok), observed=observed))
    s=seeded()
    try:
        j=submit(s); a=s.claim(j,'worker-a',0)
        record('same_intent',submit(s)==j,'same job')
        try: submit(s,raw=b'changed')
        except Conflict: rejected=True
        else: rejected=False
        record('key_conflict',rejected,'Conflict')
        s.prepare_job(a,1)
        old=Copilot(s).answer(ALICE,'returns')['answer']
        record('staging_hidden',old=='Prazo: 30 dias.' and not s.visible_chunks(ALICE,'returns'),'version 1')
        try:s.write_batch(a,2,fail=True)
        except RuntimeError:pass
        record('batch_rollback',s.job(j)['cursor']==0, s.job(j)['cursor'])
        s.write_batch(a,3)
        b=s.claim(j,'worker-b',10)
        record('checkpoint_resume',s.job(j)['cursor']==2 and b.token==2,[2,b.token])
        try:s.write_batch(a,11)
        except LostLease:rejected=True
        else:rejected=False
        record('stale_writer',rejected,'LostLease')
        stage(s,b,11)
        v=s.activate(b,12)
        record('atomic_activation',v==2 and s.job(j)['cursor']==s.job(j)['total'],v)
        record('projection_lag',not s.visible_chunks(ALICE,'returns'),'unavailable')
        s.drain()
        chunks=s.visible_chunks(ALICE,'returns')
        record('generation_visible',len(chunks)==3 and chunks[0]['body'].startswith('Prazo: 45'),len(chunks))
        record('tenant_isolation',not s.visible_chunks(BOB,'returns') and Copilot(s).answer(BOB,'returns')['answer']=='Prazo: 7 dias.','zen: version 1')
    finally:s.close()
    s=seeded()
    try:
        j=submit(s);a=s.claim(j,'worker',0);stage(s,a,1)
        s.set_acl('acme','returns',['admin'])
        s.activate(a,2)
        record('revocation_preserved',s.job(j)['state']=='obsolete' and not s.visible_chunks(ALICE,'returns'),'obsolete')
        bad=submit(s,request_id='invalid',raw=b'{')
        a=s.claim(bad,'worker',3);s.prepare_job(a,4)
        record('invalid_source',s.job(bad)['state']=='quarantined','quarantined')
    finally:s.close()
    return dict(kind='offline controlled ingestion scenarios',scenarios=rows,
                passed=sum(r['passed'] for r in rows),total=len(rows))

if __name__=='__main__':
    result=run_scenarios()
    folder=Path(__file__).with_name('results');folder.mkdir(exist_ok=True)
    (folder/'scenarios.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))
