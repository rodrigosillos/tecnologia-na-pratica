from pathlib import Path
from threading import Event
import json
from fixtures import ALICE,BOB,ingest
from job_worker import manuals
from control import Session,SimulatedPlanner,Limits,run,score

NAMES=('baseline','reverse','transient','persistent_read','premature_finish',
       'unknown_tool','extra_field','scope_escape','duplicate_read','revoked',
       'revised','budget','deadline','step_limit','cancelled','other_tenant')


def run_case(name,language='pt-BR',mode='agent'):
    if name not in NAMES:raise ValueError('case')
    store=manuals();options={};session_options={};actor=ALICE
    try:
        if name=='reverse' and mode=='agent':options['planner']=SimulatedPlanner(reverse=True)
        if name in ('transient','persistent_read'):session_options['fail_reads']=1 if name=='transient' else 3
        scripts={
          'premature_finish':[{'tool':'finish','result':'r1'}],
          'unknown_tool':[{'tool':'delete','document':'manual-a'}],
          'extra_field':[{'tool':'read','document':'manual-a','tenant':'zen'}],
          'scope_escape':[{'tool':'read','document':'payroll'}],
          'duplicate_read':[{'tool':'read','document':'manual-a'}]*3}
        if name in scripts and mode=='agent':options['planner']=SimulatedPlanner(scripts[name])
        if name=='revoked':
            options['before_action']=lambda a,s:store.set_acl('acme','manual-a',['admin']) if a['tool']=='finish' else None
        if name=='revised':
            def revise(a,s):
                if a['tool']=='finish':ingest(store,'manual-a','Devolução: prazo de 46 dias. Postagem: despacho em 3 dias.',
                    'Returns: window of 46 days. Shipping: dispatch in 3 days.',expected=1)
            options['before_action']=revise
        if name=='budget':options['limits']=Limits(units=3)
        if name=='deadline':options['limits']=Limits(ms=14)
        if name=='step_limit':options['limits']=Limits(steps=3)
        if name=='cancelled':
            event=Event();event.set();options['cancel']=event
        if name=='other_tenant':actor=BOB
        result=run(Session(store,actor,language,**session_options),mode,**options)
        return {'case':name,'language':language,'mode':mode,**result}
    finally:store.close()


def comparison():
    out={}
    for mode in ('workflow','agent'):
        runs=[run_case('transient' if i>=8 else 'baseline',mode=mode) for i in range(10)]
        out[mode]={'summary':score(runs),'runs':runs}
    return out


def run_scenarios():
    runs=[run_case(name,lang) for lang in ('pt-BR','en-US') for name in NAMES]
    return {'cases':len(runs),'language_pairs':len(NAMES),'runs':runs,'comparison':comparison(),
       'measurement':'Scripted planner, virtual time and original fictional tariffs: planning 2 u/7 ms; read 1/5; compare 1/3; finish 1/2. Not model performance, prices, or a production benchmark.'}


if __name__=='__main__':
    out=Path('results');out.mkdir(exist_ok=True)
    report=run_scenarios();(out/'scenarios.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps({k:v['summary'] for k,v in report['comparison'].items()},indent=2))
