from pathlib import Path
import json
from fixtures import ALICE, ADMIN, ingest
from job_worker import manuals
from routing import Reply, SimulatedModels, RoutePolicy
from cache_cost import AnswerCache, Ledger, Gate, execute

NAMES=('cold','hot','ttl_expired','other_user','acl_revoked',
       'source_revised','prompt_revised','corrupt_cache','partial_uncached',
       'timeout_fallback','unknown_charge','budget_denied','capacity','singleflight')


class UnknownAdapter:
    def call(self,model,saved,clock):
        raise ConnectionError('simulated loss of billing evidence')


def revise(store):
    ingest(store,'manual-a',
           'Devolução: prazo de 60 dias. Postagem: despacho em 3 dias.',
           'Returns: window of 60 days. Shipping: dispatch in 3 days.',expected=1)


def run_case(name,language):
    if name not in NAMES:raise ValueError(name)
    store=manuals();cache=AnswerCache();ledger=Ledger();gate=Gate(1)
    ledger.configure('acme',93 if name=='budget_denied' else 1000)
    params={};actor=ALICE
    def run(task,**kw):
        return execute(store,actor,cache,ledger,gate,task,language,**kw)
    try:
        if name in ('hot','ttl_expired','other_user','acl_revoked',
                    'source_revised','prompt_revised','corrupt_cache'):
            run('warm')
        if name=='ttl_expired':params['now']=1000
        if name=='other_user':actor=ADMIN
        if name=='acl_revoked':store.set_acl('acme','manual-a',['admin'])
        if name=='source_revised':revise(store)
        if name=='prompt_revised':params['prompt']='compare-v2'
        if name=='corrupt_cache':cache.db.execute("UPDATE answers SET body='{}'")
        if name=='partial_uncached':
            params=dict(policy=RoutePolicy(max_units=20),
                        adapter=SimulatedModels({'compact':Reply('partial')}))
            run('partial-1',**params)
        if name=='timeout_fallback':
            params['adapter']=SimulatedModels({'compact':Reply(elapsed_ms=500)})
        if name=='unknown_charge':params['adapter']=UnknownAdapter()
        if name=='capacity':gate.enter('another-key')
        if name=='singleflight':
            nested=[]
            params['adapter']=SimulatedModels(after_call=lambda _:nested.append(run('nested')))
            first=run('outer',**params)
            result=nested[0]
            assert first['state']=='full'
        else:result=run('request',**params)
        balance=ledger.balance('acme')
        return dict(case=name,language=language,state=result['state'],
            reason=result['reason'],hit=result['cache_hit'],calls=result['model_calls'],
            units=result['task_units'],held=balance['held'],spent=balance['spent'])
    finally:store.close();cache.close();ledger.close()


def cohort():
    outcomes={}
    for strategy in ('without_cache','with_cache'):
        store=manuals();cache=AnswerCache();ledger=Ledger();gate=Gate()
        ledger.configure('acme',1000)
        try:
            rows=[execute(store,ALICE,cache,ledger,gate,str(i),
                          use_cache=strategy=='with_cache',now=i) for i in range(10)]
            outcomes[strategy]=dict(requests=10,full=sum(r['state']=='full' for r in rows),
                hits=sum(r['cache_hit'] for r in rows),calls=sum(r['model_calls'] for r in rows),
                units=sum(r['task_units'] for r in rows),held=ledger.balance('acme')['held'])
        finally:store.close();cache.close();ledger.close()
    return outcomes


def run_scenarios():
    runs=[run_case(name,language) for language in ('pt-BR','en-US') for name in NAMES]
    return dict(cases=len(runs),language_pairs=len(NAMES),runs=runs,cohort=cohort(),
        measurement='Authored offline fixtures; fictional units; cohort intentionally repeats one authorized task. Not a load, savings, quality, or commercial price forecast.')


if __name__=='__main__':
    report=run_scenarios();Path('results').mkdir(exist_ok=True)
    Path('results/scenarios.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))
