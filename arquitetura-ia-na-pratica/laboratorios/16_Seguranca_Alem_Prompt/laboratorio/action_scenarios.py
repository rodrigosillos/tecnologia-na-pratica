from pathlib import Path
from tempfile import TemporaryDirectory
import json
from base.store import Actor
from fixtures import ALICE,ingest
from job_worker import manuals
from actions import ActionService,TaskDestination,Denied,ProcessCrash

REVIEWER=Actor('acme','carol')
DRAFT=json.dumps({'tool':'prepare_task','project':'ops','topic':'returns'})
SCRATCH=Path(__file__).resolve().parent/'scratch'
SCRATCH.mkdir(exist_ok=True)
NAMES=('pending','success','human_reject','cancelled','wrong_hash','self_approval',
       'expired','requester_revoked','reviewer_revoked','source_revoked','revised',
       'timeout_before','timeout_after','reconcile_after','retry_before',
       'crash_before','restart_after','attempt_limit')


def fixture(path=':memory:',destination=':memory:'):
    store=manuals();service=ActionService(store,path);dest=TaskDestination(destination)
    service.grant(ALICE,'requester');service.grant(REVIEWER,'reviewer')
    return store,service,dest


def approve(service,id,now=1):
    view=service.preview(REVIEWER,id)
    return service.decide(REVIEWER,id,view['hash'],True,now)


def run_case(name,language='pt-BR'):
    if name not in NAMES:raise ValueError('case')
    with TemporaryDirectory(dir=SCRATCH) as tmp:
        path=Path(tmp)/'actions.db';provider=Path(tmp)/'destination.db'
        store,s,d=fixture(path,provider);error=None;total_calls=0;total_lookups=0
        try:
            id=s.propose(ALICE,DRAFT,language=language)
            if name=='wrong_hash':
                try:s.decide(REVIEWER,id,'0'*64,True)
                except Denied as e:error=str(e)
            elif name=='self_approval':
                try:s.decide(ALICE,id,s.row(id)['hash'],True)
                except Denied as e:error=str(e)
            elif name=='human_reject':s.decide(REVIEWER,id,s.row(id)['hash'],False)
            elif name=='cancelled':s.cancel(ALICE,id)
            elif name!='pending':
                approve(s,id)
                if name=='requester_revoked':s.grant(ALICE,'requester',False)
                if name=='reviewer_revoked':s.grant(REVIEWER,'reviewer',False)
                if name=='source_revoked':store.set_acl('acme','manual-a',['admin'])
                if name=='revised':ingest(store,'manual-a','Devolução: prazo de 46 dias. Postagem: despacho em 3 dias.',
                    'Returns: window of 46 days. Shipping: dispatch in 3 days.',expected=1)
                fault='before' if name in ('timeout_before','retry_before','attempt_limit') else (
                    'after' if name in ('timeout_after','reconcile_after') else None)
                crash='before' if name=='crash_before' else ('after' if name=='restart_after' else None)
                try:s.dispatch(id,d,now=30 if name=='expired' else 2,fault=fault,crash=crash)
                except ProcessCrash:pass
                if name in ('crash_before','restart_after'):
                    total_calls+=d.calls;total_lookups+=d.lookups;s.close();d.close()
                    s=ActionService(store,path);d=TaskDestination(provider)
                    s.recover(id);s.reconcile(id,d,4,retry=True)
                if name=='reconcile_after':s.reconcile(id,d)
                if name=='retry_before':s.reconcile(id,d,retry=True)
                if name=='attempt_limit':
                    s.dispatch(id,d,3,fault='before',retry=True)
                    s.reconcile(id,d,4,retry=True)
            row=s.row(id)
            return {'case':name,'language':language,'state':row['state'],'reason':error or row['reason'],
                'attempts':row['attempts'],'create_calls':total_calls+d.calls,
                'lookups':total_lookups+d.lookups,'effects':d.count(),'has_receipt':row['receipt'] is not None,
                'events':[r['event'] for r in s.events(id)]}
        finally:s.close();d.close();store.close()


def run_scenarios():
    runs=[run_case(name,lang) for lang in ('pt-BR','en-US') for name in NAMES]
    return {'cases':len(runs),'language_pairs':len(NAMES),'runs':runs,
        'measurement':'Local SQLite intent and separate simulated destination; virtual integer seconds, no external effects or network. Serial execution; restart closes and reopens connections. Not a production benchmark.'}


if __name__=='__main__':
    out=Path('results');out.mkdir(exist_ok=True)
    result=run_scenarios();(out/'scenarios.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))
