"""Versioned evaluation of controlled systems; no model quality benchmark."""
from pathlib import Path
from dataclasses import asdict
import argparse, csv, hashlib, json, math, random, sys
from systems import System, Request, ROOT


def load_cases(path=ROOT/'cases.v1.json'):
    data=json.loads(Path(path).read_text(encoding='utf-8'))
    cases=data['cases']
    if not cases:raise ValueError('empty evaluation')
    ids=[c['id'] for c in cases]
    if len(ids)!=len(set(ids)):raise ValueError('duplicate case id')
    splits={}
    for case in cases:
        if case['expected']['decision'] not in ('answer','abstain','human_review'):
            raise ValueError('unknown expected decision')
        if case['input']['language'] not in ('pt-BR','en-US'):
            raise ValueError('unknown language')
        group=case['group']
        splits.setdefault(group,set()).add(case['split'])
    if any(len(s)>1 for s in splits.values()):
        raise ValueError('same group crosses splits')
    return data


def decision(outcome):
    if outcome.status=='abstain' and outcome.reason=='conflicting_evidence':
        return 'human_review'
    if outcome.status=='error':return 'operational_error'
    return outcome.status


def task_passes(expected, observed):
    if decision(observed)!=expected['decision']:
        return False
    if expected['decision']=='answer':
        return (observed.answer==expected['answer']
                and observed.citation in expected['citations']
                and observed.reason is None)
    return (observed.answer is None and observed.citation is None
            and observed.reason==expected['reason'])


def exposure(case, observed, documents):
    if observed.citation is None:return False
    doc=documents.get(observed.citation)
    if doc is None:return False  # Unsupported citation is a different failure.
    request=case['input']
    return (doc['tenant']!=request['tenant']
            or request['role'] not in doc['roles'])


def ratio(numerator, denominator):
    return None if denominator==0 else numerator/denominator


def percentile(values, q):
    if not values:return None
    if not 0<=q<=1:raise ValueError('invalid quantile')
    values=sorted(values)
    # Nearest-rank convention; q=0 is the minimum.
    return values[max(0,math.ceil(q*len(values))-1)]


def summarize(rows):
    eligible=[r for r in rows if r['expected_decision']=='answer']
    answered=[r for r in rows if r['decision']=='answer']
    correct=[r for r in answered if r['task_pass']]
    known=[r['cost_microusd'] for r in rows if r['cost_microusd'] is not None]
    return {'cases':len(rows),'task_passes':sum(r['task_pass'] for r in rows),
        'task_success':ratio(sum(r['task_pass'] for r in rows),len(rows)),
        'eligible':len(eligible),'answers':len(answered),'correct_answers':len(correct),
        'answer_precision':ratio(len(correct),len(answered)),
        'answer_recall':ratio(len(correct),len(eligible)),
        'answer_coverage':ratio(sum(r['decision']=='answer' for r in eligible),len(eligible)),
        'exposures':sum(r['exposure'] for r in rows),
        'known_cost_microusd':sum(known),'unknown_cost_cases':len(rows)-len(known),
        'cost_per_correct_answer':(ratio(sum(known),len(correct))
                                  if len(known)==len(rows) else None),
        'p95_ms':percentile([r['elapsed_ms'] for r in rows],.95)}


def gate(summary, slices, policy):
    failures=[]
    if summary['cases']!=policy['expected_cases']:
        failures.append('case_count')
    if summary['exposures']>0:failures.append('exposure')
    for metric in ('task_success','answer_recall'):
        value=summary[metric]
        if value is None or value<policy['minimum'][metric]:
            failures.append(metric)
    if summary['unknown_cost_cases']:
        failures.append('unknown_cost')
    for metric,ceiling in policy['maximum'].items():
        value=summary[metric]
        if value is None or value>ceiling:
            failures.append(metric)
    for name in policy['required_slices']:
        part=slices.get(name)
        if part is None or part['task_success'] is None:
            failures.append('missing_slice:'+name)
        elif part['task_success']<policy['minimum']['slice_success']:
            failures.append('slice:'+name)
    return {'passed':not failures,'failures':failures}


def run_suite(mode, data=None):
    data=load_cases() if data is None else data
    docs={d['id']:d for d in json.loads((ROOT/'app/documents.json').read_text(encoding='utf-8'))}
    system=System(mode)
    rows=[]
    for case in data['cases']:
        output=system.run(Request(**case['input']))
        passed=task_passes(case['expected'],output)
        leaked=exposure(case,output,docs)
        rows.append({'id':case['id'],'group':case['group'],
            'language':case['input']['language'],'tenant':case['input']['tenant'],
            'category':case['category'],'expected_decision':case['expected']['decision'],
            'decision':decision(output),'task_pass':passed and not leaked,
            'exposure':leaked,'cost_microusd':output.cost_microusd,
            'elapsed_ms':output.elapsed_ms,'observed':asdict(output)})
    summary=summarize(rows)
    slices={}
    for key in ('language','tenant','category'):
        for value in sorted({r[key] for r in rows}):
            slices[f'{key}:{value}']=summarize([r for r in rows if r[key]==value])
    policy=json.loads((ROOT/'policy.v1.json').read_text(encoding='utf-8'))
    return {'system':mode,'summary':summary,'slices':slices,
            'gate':gate(summary,slices,policy),'rows':rows}


def paired_groups(left, right):
    a={r['id']:r for r in left['rows']};b={r['id']:r for r in right['rows']}
    if len(a)!=len(left['rows']) or len(b)!=len(right['rows']):
        raise ValueError('duplicate result id')
    if a.keys()!=b.keys():raise ValueError('unpaired cases')
    groups={}
    for key in sorted(a):
        if a[key]['group']!=b[key]['group']:raise ValueError('group mismatch')
        groups.setdefault(a[key]['group'],[]).append(
            int(b[key]['task_pass'])-int(a[key]['task_pass']))
    return [sum(v)/len(v) for _,v in sorted(groups.items())]


def bootstrap_delta(left, right, draws=2000, seed=7):
    values=paired_groups(left,right)
    if len(values)<2 or draws<100:raise ValueError('insufficient resampling')
    rng=random.Random(seed)
    means=[sum(rng.choices(values,k=len(values)))/len(values)
           for _ in range(draws)]
    return {'unit':'group','groups':len(values),'draws':draws,'seed':seed,
            'delta':sum(values)/len(values),
            'lower':percentile(means,.025),'upper':percentile(means,.975),
            'scope':'descriptive bootstrap on this synthetic fixture only'}


def manifest():
    paths=sorted([*ROOT.glob('*.py'),*ROOT.glob('*.json'),
                  * (ROOT/'app').glob('*.py'),* (ROOT/'app').glob('*.json')])
    return {'dataset_version':'cases.v1','policy_version':'policy.v1',
            'python':sys.version.split()[0],
            'sha256':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in paths}}


def review_packet(out, reports):
    """Unrated blind-format worksheet; no claim of actual human review."""
    rng=random.Random(41);rows={'pt-BR':[],'en-US':[]};key=[]
    inputs={c['id']:c['input'] for c in load_cases()['cases']}
    for a,b in zip(reports['baseline']['rows'],reports['fast_unsafe']['rows']):
        pair=[a,b];rng.shuffle(pair)
        def content(row):
            return {k:row['observed'][k] for k in ('status','answer','citation','reason')}
        rows[a['language']].append({'case_id':a['id'],'group':a['group'],
            'request':json.dumps(inputs[a['id']],ensure_ascii=False),
            'A':json.dumps(content(pair[0]),ensure_ascii=False),
            'B':json.dumps(content(pair[1]),ensure_ascii=False),
            'verdict':'','evidence':'','severity':'','reviewer':''})
        key.append({'case_id':a['id'],'A':'baseline' if pair[0] is a else 'fast_unsafe'})
    for lang,name in [('pt-BR','revisao_humana_pt.csv'),('en-US','human_review_en.csv')]:
        with (out/name).open('w',encoding='utf-8-sig',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=rows[lang][0].keys())
            writer.writeheader();writer.writerows(rows[lang])
    (out/'chave_revisao.json').write_text(json.dumps(key,indent=2),encoding='utf-8')


def evaluate():
    reports={mode:run_suite(mode) for mode in System.MODES}
    return {'measurement_kind':'controlled_stubs_synthetic_cost_and_time',
        'reports':reports,'comparison':bootstrap_delta(reports['baseline'],reports['fast_unsafe']),
        'manifest':manifest()}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,default=ROOT/'results')
    args=parser.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    result=evaluate()
    (args.out/'evaluation.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    review_packet(args.out,result['reports'])
    for mode,report in result['reports'].items():
        print(mode,report['summary']['task_passes'],'/',report['summary']['cases'],report['gate'])
