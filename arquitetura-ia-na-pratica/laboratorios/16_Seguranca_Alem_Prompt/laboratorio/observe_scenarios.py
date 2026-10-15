from pathlib import Path
import json
from cache_cost import AnswerCache,Ledger,Gate,execute
from cache_scenarios import UnknownAdapter
from fixtures import ALICE,BOB
from job_worker import manuals
from routing import RoutePolicy,Reply,SimulatedModels
from observability import observe,MemoryExporter,Measurements,stage_totals

NAMES=('baseline','cached','queue_slow','source_slow','fallback','partial',
       'refusal','unknown_cost','budget','access','quality_missing','export_down')


def run_case(name,language='pt-BR',trace_output=False):
    if name not in NAMES:raise ValueError('case')
    store=manuals();cache=AnswerCache();ledger=Ledger();gate=Gate()
    ledger.configure('acme',93 if name=='budget' else 1000)
    options={};actor=ALICE
    try:
        if name=='cached':execute(store,actor,cache,ledger,gate,'warm',language)
        if name=='queue_slow':options['queue_ms']=80
        if name=='source_slow':options['source_ms']=12
        if name=='fallback':options['adapter']=SimulatedModels({'compact':Reply('transient')})
        if name=='partial':
            options.update(policy=RoutePolicy(max_units=20),adapter=SimulatedModels({'compact':Reply('partial')}))
        if name=='refusal':options['adapter']=SimulatedModels({'compact':Reply('refusal')})
        if name=='unknown_cost':options['adapter']=UnknownAdapter()
        if name=='access':actor=BOB;options['eligible']=False
        if name=='quality_missing':options['assessed']=False
        if name=='export_down':options['exporter']=MemoryExporter(fail=True)
        row,trace=observe(store,actor,cache,ledger,gate,name,language,**options)
        public=dict(case=name,language=language,state=row['state'],quality=row['quality'],
            duration_ms=row['duration_ms'],queue_ms=row['queue_ms'],calls=row['calls_started'],
            settled=row['settled_units'],held=row['held_units'],export_failures=row['export_failures'],
            stages=stage_totals(trace))
        if trace_output:return row,trace
        return public
    finally:store.close();cache.close();ledger.close()


def regression():
    out={}
    for variant in ('baseline','regression','queue_only'):
        metrics=Measurements();exporter=MemoryExporter();stages={}
        for i in range(20):
            store=manuals();cache=AnswerCache();ledger=Ledger();gate=Gate()
            ledger.configure('acme',1000)
            try:
                fallback=variant=='regression' and i>=15
                adapter=SimulatedModels({'compact':Reply('transient')}) if fallback else None
                row,trace=observe(store,ALICE,cache,ledger,gate,f'{variant}-{i}',
                    release='r1' if variant=='baseline' else 'r2',
                    queue_ms=0 if variant=='baseline' else 80,sampled=i%4==0,
                    exporter=exporter,adapter=adapter)
                metrics.add(row)
                for k,v in stage_totals(trace).items():stages[k]=stages.get(k,0)+v
            finally:store.close();cache.close();ledger.close()
        out[variant]={'summary':metrics.summary(),'retained_traces':len(exporter.traces),
            'stage_total_ms':stages,'rows':list(metrics.rows.values())}
    return out


def run_scenarios():
    runs=[run_case(n,lang) for lang in ('pt-BR','en-US') for n in NAMES]
    return dict(cases=len(runs),language_pairs=len(NAMES),runs=runs,regression=regression(),
        measurement='Original offline fixture: source reads 3 ms (12 in fault), lookup 2, write/admission/settlement 1, router finalization 20, scripted model time; virtual queue delay. No latency or SLO claim about a deployed system.')


if __name__=='__main__':
    out=Path('results');out.mkdir(exist_ok=True)
    report=run_scenarios();(out/'scenarios.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    _,trace=run_case('fallback',trace_output=True)
    (out/'example_trace.json').write_text(json.dumps(trace.exporter.traces[0],indent=2),encoding='utf-8')
    print(json.dumps({k:v['summary'] for k,v in report['regression'].items()},indent=2))
