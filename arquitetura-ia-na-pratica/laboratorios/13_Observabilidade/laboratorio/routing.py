"""Original offline routing lab. Registry and charges are fictional, not prices."""
from dataclasses import dataclass
import copy
import json
from threading import Event
from job_worker import capture, compare, still_valid
from resilience import Clock

OPERATION='compare-manuals-v1'
POLICY_VERSION='route-v1'
TOPICS=('returns','shipping')


@dataclass(frozen=True)
class Model:
    name: str
    revision: str='r1'
    zone: str='local'
    languages: tuple=('pt-BR','en-US')
    capabilities: tuple=(OPERATION,)
    context_bytes: int=8192
    units: int=20
    timeout_ms: int=60


@dataclass(frozen=True)
class RoutePolicy:
    zones: tuple=('local',)
    max_units: int=90
    budget_ms: int=220
    reserve_ms: int=20
    max_calls: int=2
    allow_partial: bool=True

    def __post_init__(self):
        for name in ('max_units','budget_ms','reserve_ms','max_calls'):
            value=getattr(self,name)
            if type(value) is not int or value<0:raise ValueError(name)
        if self.reserve_ms>self.budget_ms:raise ValueError('reserve')
        if type(self.allow_partial) is not bool:raise ValueError('partial')
        if not self.zones or any(z not in ('local','external') for z in self.zones):
            raise ValueError('zones')


def registry():
    return (Model('compact'),Model('large',units=70,timeout_ms=140),
            Model('remote',zone='external',units=10,timeout_ms=40))


def approvals(models):
    # Authored fixtures, not quality measurements or confidence estimates.
    return frozenset((m.name,m.revision,OPERATION,lang)
                     for m in models for lang in m.languages)


def rejection(model, language, size, policy, approved):
    if model.zone not in policy.zones:return 'privacy'
    if OPERATION not in model.capabilities:return 'capability'
    if language not in model.languages:return 'language'
    scope=(model.name,model.revision,OPERATION,language)
    if scope not in approved:return 'unapproved'
    if size>model.context_bytes:return 'context'
    return None


def fits(model, units_left, ms_left, policy):
    return (model.units<=units_left and
            model.timeout_ms+policy.reserve_ms<=ms_left)


def validate_rows(packet, expected):
    if type(packet) is not dict or set(packet)!={'schema_version','rows'}:
        return None
    if packet['schema_version']!='1.0':return None
    rows=packet['rows']
    if type(rows) is not list or not 0<len(rows)<=len(expected):
        return None
    seen=set()
    for row in rows:
        if type(row) is not dict or set(row)!=set(expected[0]):
            return None
        if type(row['topic']) is not str or row['topic'] in seen:
            return None
        seen.add(row['topic'])
        if any(type(row[k]) is not int for k in ('left','right','delta')):
            return None
        if type(row['same']) is not bool:return None
        gold=next((r for r in expected if r['topic']==row['topic']),None)
        if row!=gold:return None
    return sorted(copy.deepcopy(rows),
                  key=lambda r:TOPICS.index(r['topic']))


@dataclass(frozen=True)
class Reply:
    outcome: str='full'
    elapsed_ms: int=40


class SimulatedModels:
    def __init__(self, replies=None, after_call=None):
        self.replies=replies or {};self.after_call=after_call;self.calls=[]

    def call(self,model,saved,clock):
        default_ms={'compact':40,'large':90,'remote':20}[model.name]
        reply=self.replies.get(model.name,Reply(elapsed_ms=default_ms))
        if type(reply.elapsed_ms) is not int or reply.elapsed_ms<0:
            raise ValueError('elapsed_ms')
        self.calls.append(model.name)
        clock.advance(min(reply.elapsed_ms,model.timeout_ms))
        if self.after_call:self.after_call(model.name)
        if reply.elapsed_ms>=model.timeout_ms:return 'timeout',None
        if reply.outcome in ('transient','refusal','fatal'):
            return reply.outcome,None
        if reply.outcome not in ('full','partial','wrong','invalid'):
            raise ValueError('unknown simulated reply')
        rows=compare(saved)['rows']
        if reply.outcome=='partial':rows=rows[:1]
        if reply.outcome=='wrong':rows[0]['delta']=15
        packet=dict(schema_version='1.0',rows=rows)
        if reply.outcome=='invalid':packet['extra']='not allowed'
        return 'ok',packet


def sources_valid(store, actor, saved, language):
    store.db.execute('BEGIN')
    try:return all(still_valid(store,actor,s,language) for s in saved)
    finally:store.db.execute('COMMIT')


def route(store, actor, language='pt-BR', documents=('manual-a','manual-b'),
          policy=None, models=None, approved=None, adapter=None,
          disabled=(), clock=None, deadline_ms=None, cancel=None):
    policy=policy or RoutePolicy();models=tuple(models if models is not None else registry())
    if language not in ('pt-BR','en-US'):raise ValueError('language')
    if len(documents)!=2 or len(set(documents))!=2:raise ValueError('documents')
    if len({m.name for m in models})!=len(models):raise ValueError('duplicate model')
    for m in models:
        if any(type(getattr(m,k)) is not int or getattr(m,k)<=0
               for k in ('units','timeout_ms','context_bytes')):
            raise ValueError('invalid registry')
    # Default approvals apply only to the original fixture revisions.
    approved=approvals(registry()) if approved is None else frozenset(approved)
    adapter=adapter or SimulatedModels();clock=clock or Clock();cancel=cancel or Event()
    start=clock.now
    if deadline_ms is not None and type(deadline_ms) is not int:
        raise ValueError('deadline_ms')
    deadline=min(start+policy.budget_ms,deadline_ms if deadline_ms is not None else start+policy.budget_ms)
    trace=[];charged=0;attempts=0;best=[];selected=None

    def finish(state,reason,rows=(),chosen=None):
        # A fixed synthetic finalization duration, reserved before each call.
        if attempts:clock.advance(policy.reserve_ms)
        if cancel.is_set():state,reason,rows,chosen='abstain','cancelled',(),None
        if clock.now>deadline:state,reason,rows,chosen='abstain','deadline',(),None
        if rows and not sources_valid(store,actor,saved,language):
            state,reason,rows,chosen='abstain','source_changed',(),None
        topics={r['topic'] for r in rows}
        sources=[dict(document=s['snapshot']['document'],version=s['snapshot']['version'],
                      source=s['snapshot']['source'],
                      quotes=[s['facts'][t]['quote'] for t in TOPICS if t in topics])
                 for s in saved] if rows else []
        return dict(policy_version=POLICY_VERSION,state=state,reason=reason,
            language=language,model=chosen,rows=list(rows),sources=sources,
            missing=[t for t in TOPICS if t not in topics],calls=attempts,
            charged_units=charged,elapsed_ms=clock.now-start,trace=trace)

    saved=[]
    if cancel.is_set():return finish('abstain','cancelled')
    if deadline<=start:return finish('abstain','deadline')
    store.db.execute('BEGIN')
    try:
        saved=[capture(store,actor,d,language) for d in documents]
    except ValueError:return finish('abstain','source_unavailable')
    finally:store.db.execute('COMMIT')
    size=len(json.dumps(saved,ensure_ascii=False,sort_keys=True).encode('utf-8'))
    expected=compare(saved)['rows']
    reason='no_eligible_model'
    for model in sorted(models,key=lambda m:(m.units,m.name)):
        why=rejection(model,language,size,policy,approved)
        if not why and model.name in disabled:why='disabled'
        if why:
            trace.append(dict(model=model.name,event='skip',reason=why));continue
        if attempts>=policy.max_calls:reason='call_limit';break
        if cancel.is_set():return finish('abstain','cancelled')
        if not sources_valid(store,actor,saved,language):
            return finish('abstain','source_changed')
        if not fits(model,policy.max_units-charged,deadline-clock.now,policy):
            reason='budget_or_deadline'
            trace.append(dict(model=model.name,event='skip',reason=reason));continue
        charged+=model.units;attempts+=1
        status,packet=adapter.call(model,saved,clock)
        trace.append(dict(model=model.name,revision=model.revision,event='call',
                          reason=status,units=model.units))
        if status in ('refusal','fatal'):
            return finish('abstain',status)
        if status!='ok':reason=status;continue
        rows=validate_rows(packet,expected)
        if rows is None:
            trace[-1]['reason']='invalid_output';reason='invalid_output';continue
        if len(rows)==len(TOPICS):return finish('full','validated',rows,model.name)
        trace[-1]['reason']='validated_partial';reason='incomplete'
        if len(rows)>len(best):best,selected=rows,model.name
    if best and policy.allow_partial:return finish('partial',reason,best,selected)
    return finish('abstain',reason)
