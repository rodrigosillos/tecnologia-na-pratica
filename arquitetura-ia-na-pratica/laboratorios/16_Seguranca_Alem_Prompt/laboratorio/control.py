"""Offline Chapter 14. Scripted planner, typed read-only tools, synthetic units."""
from dataclasses import dataclass
from threading import Event
import copy,json,re
from job_worker import capture,compare
from routing import sources_valid
from observability import percentile

FIELDS={'read':{'tool','document'},'compare':{'tool','left','right'},
        'finish':{'tool','result'},'stop':{'tool','reason'}}
TARIFF={'read':(1,5),'compare':(1,3),'finish':(1,2),'stop':(0,0)}


def unique_object(pairs):
    out={}
    for key,value in pairs:
        if key in out:raise ValueError('duplicate key')
        out[key]=value
    return out


def parse_action(raw):
    if type(raw) is not str or len(raw.encode('utf-8'))>512:
        raise ValueError('action size')
    action=json.loads(raw,object_pairs_hook=unique_object)
    if type(action) is not dict:raise ValueError('action object')
    tool=action.get('tool')
    if type(tool) is not str or tool not in FIELDS:
        raise ValueError('tool')
    if set(action)!=FIELDS[tool]:raise ValueError('fields')
    for key,value in action.items():
        if type(value) is not str or not 0<len(value)<=64:
            raise ValueError('value')
    if tool=='stop' and action['reason']!='no_evidence':
        raise ValueError('reason')
    return action


@dataclass(frozen=True)
class Limits:
    steps:int=8
    units:int=30
    ms:int=150
    repeats:int=2
    def __post_init__(self):
        for key in ('steps','units','ms','repeats'):
            if type(getattr(self,key)) is not int or getattr(self,key)<0:
                raise ValueError('limits')
        if self.repeats<1:raise ValueError('repeats')


class Halt(Exception):pass


class Meter:
    def __init__(self,limits):self.limits=limits;self.units=0;self.ms=0
    def spend(self,units,ms):
        if self.units+units>self.limits.units:raise Halt('budget')
        if self.ms+ms>self.limits.ms:raise Halt('deadline')
        self.units+=units;self.ms+=ms


class Session:
    def __init__(self,store,actor,language='pt-BR',documents=('manual-a','manual-b'),fail_reads=0):
        if language not in ('pt-BR','en-US'):raise ValueError('language')
        if len(documents)!=2 or len(set(documents))!=2:raise ValueError('documents')
        if any(type(d) is not str or not re.fullmatch('[a-z0-9-]{1,48}',d) for d in documents):
            raise ValueError('documents')
        if type(fail_reads) is not int or fail_reads<0:raise ValueError('fail_reads')
        self.store=store;self.actor=actor;self.language=language;self.documents=tuple(documents)
        self.saved={};self.by_doc={};self.result=None;self.output=None;self.fail_reads=fail_reads
        self.read_failures=0;self.events=[];self.used=False
    def view(self):
        return {'remaining':[d for d in self.documents if d not in self.by_doc],
                'handles':[self.by_doc[d] for d in self.documents if d in self.by_doc],
                'result':'r1' if self.result is not None else None,
                'read_failures':self.read_failures}
    def invoke(self,a):
        tool=a['tool']
        if tool=='stop':raise Halt('no_evidence')
        if tool=='read':
            document=a['document']
            if document not in self.documents:raise Halt('scope')
            if document in self.by_doc:return 'unchanged'
            if self.fail_reads:
                self.fail_reads-=1;self.read_failures+=1;return 'transient'
            try:value=capture(self.store,self.actor,document,self.language)
            except ValueError:raise Halt('unavailable') from None
            handle='e'+str(len(self.saved)+1)
            self.saved[handle]=value;self.by_doc[document]=handle
            return 'captured'
        if tool=='compare':
            expected=[self.by_doc.get(d) for d in self.documents]
            if None in expected or [a['left'],a['right']]!=expected:
                raise Halt('evidence')
            values=[self.saved[h] for h in expected]
            if not sources_valid(self.store,self.actor,values,self.language):
                raise Halt('stale')
            self.result=compare(values);return 'compared'
        if a['result']!='r1' or self.result is None:raise Halt('evidence')
        values=[self.saved[self.by_doc[d]] for d in self.documents]
        if not sources_valid(self.store,self.actor,values,self.language):
            raise Halt('stale')
        self.output=copy.deepcopy(self.result)
        self.output['sources']=[{'document':v['snapshot']['document'],
              'version':v['snapshot']['version'],'source':v['snapshot']['source']} for v in values]
        return 'complete'


def next_action(view):
    if view['read_failures']>1:
        return {'tool':'stop','reason':'no_evidence'}
    if view['remaining']:
        return {'tool':'read','document':view['remaining'][0]}
    if view['result'] is None:
        return {'tool':'compare','left':view['handles'][0],
                'right':view['handles'][1]}
    return {'tool':'finish','result':view['result']}


class FixedWorkflow:
    """Host-authored state transitions, with one bounded read retry."""
    def next(self,view):return json.dumps(next_action(view))


class SimulatedPlanner(FixedWorkflow):
    """Scripted decisions emulate a model boundary; no LLM or learned policy."""
    def __init__(self,script=(),reverse=False):self.script=list(script);self.reverse=reverse
    def next(self,view):
        if self.script:
            action=self.script.pop(0)
            return action if type(action) is str else json.dumps(action)
        if self.reverse and view['remaining']:
            return json.dumps({'tool':'read','document':view['remaining'][-1]})
        return super().next(view)


def repeated(action,seen,limit):
    key=json.dumps(action,sort_keys=True,separators=(',',':'))
    seen[key]=seen.get(key,0)+1
    return seen[key]>limit


def run(session,mode='workflow',planner=None,limits=None,cancel=None,before_action=None):
    if mode not in ('workflow','agent'):raise ValueError('mode')
    if planner is not None and mode=='workflow':raise ValueError('planner mode')
    if session.used:raise ValueError('one execution per session')
    session.used=True
    limits=limits or Limits();meter=Meter(limits);cancel=cancel or Event()
    decision=FixedWorkflow() if mode=='workflow' else (planner or SimulatedPlanner())
    seen={};steps=0;planning_calls=0;tool_calls=0;reason='steps';state='stopped'
    try:
        while steps<limits.steps:
            if cancel.is_set():raise Halt('cancelled')
            if mode=='agent':
                meter.spend(2,7);planning_calls+=1
            try:raw=decision.next(copy.deepcopy(session.view()))
            except Exception:raise Halt('planner_error') from None
            steps+=1
            if cancel.is_set():raise Halt('cancelled')
            try:action=parse_action(raw)
            except (ValueError,TypeError,RecursionError):raise Halt('invalid_action') from None
            if repeated(action,seen,limits.repeats):raise Halt('repeated')
            if before_action:before_action(action,session)
            if cancel.is_set():raise Halt('cancelled')
            meter.spend(*TARIFF[action['tool']])
            tool_calls+=1
            status=session.invoke(action)
            session.events.append({'step':steps,'tool':action['tool'],'status':status})
            if status=='complete':state='complete';reason='validated';break
    except Halt as e:reason=str(e)
    return {'state':state,'reason':reason,'steps':steps,'planning_calls':planning_calls,
            'tool_calls':tool_calls,'units':meter.units,'duration_ms':meter.ms,
            'output':copy.deepcopy(session.output),'events':copy.deepcopy(session.events)}


def score(runs):
    complete=sum(r['state']=='complete' for r in runs)
    units=sum(r['units'] for r in runs)
    return {'requests':len(runs),'complete':complete,'units':units,
            'units_per_complete':units/complete if complete else None,
            'planning_calls':sum(r['planning_calls'] for r in runs),
            'tool_calls':sum(r['tool_calls'] for r in runs),
            'p95_ms':percentile([r['duration_ms'] for r in runs],.95)}
