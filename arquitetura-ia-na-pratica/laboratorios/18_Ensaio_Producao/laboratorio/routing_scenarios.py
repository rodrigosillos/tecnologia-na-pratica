"""Bilingual policy regression, not a benchmark of real models."""
from dataclasses import replace
from pathlib import Path
import json
from fixtures import ALICE
from job_worker import manuals
from routing import (registry,approvals,RoutePolicy,Reply,SimulatedModels,route,OPERATION)

NAMES=('compact_success','transient_fallback','invalid_fallback','wrong_fallback',
       'partial_then_full','partial_budget','partial_disabled','refusal',
       'private_no_route','language_unapproved','context_skip','deadline',
       'timeout_fallback','revoked')


def run_case(name,language='pt-BR'):
    if name not in NAMES:raise ValueError(name)
    store=manuals();models=registry();approved=approvals(models)
    policy=RoutePolicy();replies={};disabled=();hook=None
    if name in ('transient_fallback','invalid_fallback','wrong_fallback'):
        replies['compact']=Reply(name.split('_')[0])
    if name in ('partial_then_full','partial_budget','partial_disabled','deadline'):
        replies['compact']=Reply('partial')
    if name in ('partial_budget','partial_disabled'):
        policy=replace(policy,max_units=20,allow_partial=name=='partial_budget')
    if name=='refusal':replies['compact']=Reply('refusal')
    if name=='private_no_route':disabled=('compact','large')
    if name=='language_unapproved':
        approved=approved-{('compact','r1',OPERATION,language)}
    if name=='context_skip':models=(replace(models[0],context_bytes=1),*models[1:])
    if name=='deadline':policy=replace(policy,budget_ms=100)
    if name=='timeout_fallback':replies['compact']=Reply(elapsed_ms=500)
    if name=='revoked':hook=lambda _:store.set_acl('acme','manual-a',['admin'])
    adapter=SimulatedModels(replies,hook)
    try:
        result=route(store,ALICE,language,policy=policy,models=models,
                     approved=approved,adapter=adapter,disabled=disabled)
        return dict(case=name,language=language,state=result['state'],reason=result['reason'],
            models=adapter.calls,calls=result['calls'],units=result['charged_units'],
            virtual_ms=result['elapsed_ms'],rows=len(result['rows']),missing=result['missing'])
    finally:store.close()


def run_scenarios():
    runs=[run_case(n,lang) for lang in ('pt-BR','en-US') for n in NAMES]
    return dict(cases=len(runs),language_pairs=len(NAMES),runs=runs,
        cohort=cohort(),
        measurement='Authored simulated replies, fictional admission units, virtual milliseconds; no model quality or monetary benchmark')


def cohort():
    results={}
    for strategy in ('cascade','large_only'):
        reports=[]
        for i in range(10):
            store=manuals()
            try:
                adapter=SimulatedModels({'compact':Reply('partial' if i>=8 else 'full')})
                models=registry() if strategy=='cascade' else (registry()[1],)
                reports.append(route(store,ALICE,models=models,adapter=adapter))
            finally:store.close()
        results[strategy]=dict(requests=10,full=sum(r['state']=='full' for r in reports),
            calls=sum(r['calls'] for r in reports),units=sum(r['charged_units'] for r in reports),
            total_virtual_ms=sum(r['elapsed_ms'] for r in reports))
    return results


if __name__=='__main__':
    report=run_scenarios();out=Path('results');out.mkdir(exist_ok=True)
    (out/'scenarios.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))
