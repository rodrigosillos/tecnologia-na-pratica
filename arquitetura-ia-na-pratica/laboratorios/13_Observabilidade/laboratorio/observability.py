"""Original offline telemetry exercise; not an OpenTelemetry implementation."""
from contextlib import contextmanager
import copy, hashlib, math, re
from cache_cost import execute, cached_valid, snapshot
from routing import SimulatedModels

LABELS={'language':{'pt-BR','en-US'},'release':{'r1','r2'},
        'model':{'compact','large','remote'},
        'state':{'full','partial','abstain','deferred'},
        'quality':{'pass','fail','unknown'},'cache':{'hit','miss'}}
NAMES={'request','queue.wait','source.read','cache.lookup','cache.write',
       'ledger.reserve','ledger.settle','ledger.uncertain','gate.enter',
       'model.call','finalize','job.run'}


def safe_attributes(attributes):
    safe={};dropped=0
    for key,value in attributes.items():
        if key in LABELS and type(value) is str and value in LABELS[key]:
            safe[key]=value
        else:dropped+=1
    return safe,dropped


def percentile(values, p):
    if not 0<p<=1:raise ValueError('percentile')
    if any(type(v) not in (int,float) or not math.isfinite(v) or v<0
           for v in values):raise ValueError('duration')
    if not values:return None
    ordered=sorted(values)
    return ordered[math.ceil(p*len(ordered))-1]


def histogram(values, bounds=(25,50,100,200,500)):
    if not bounds or tuple(sorted(set(bounds)))!=tuple(bounds):
        raise ValueError('bounds')
    percentile(list(bounds),1);percentile(values,1)
    return {'bounds':list(bounds),'counts':[sum(v<=b for v in values) for b in bounds],
            'infinity':len(values),'count':len(values),'sum':sum(values)}


def merge_histograms(parts):
    if not parts:raise ValueError('empty')
    bounds=parts[0]['bounds']
    if any(p['bounds']!=bounds for p in parts):raise ValueError('bounds differ')
    return {'bounds':list(bounds),
            'counts':[sum(p['counts'][i] for p in parts) for i in range(len(bounds))],
            'infinity':sum(p['infinity'] for p in parts),
            'count':sum(p['count'] for p in parts),'sum':sum(p['sum'] for p in parts)}


def burn_rate(bad, eligible, target=.99):
    if type(bad) is not int or type(eligible) is not int:
        raise ValueError('counts')
    if not 0<=bad<=eligible or not 0<target<1:raise ValueError('slo')
    if eligible==0:return None
    return round((bad/eligible)/(1-target),6)


class VirtualClock:
    def __init__(self):self.now=0
    def advance(self,ms):
        if type(ms) is not int or ms<0:raise ValueError('time')
        self.now+=ms


class MemoryExporter:
    def __init__(self,fail=False):self.fail=fail;self.traces=[]
    def export(self,trace):
        if self.fail:raise OSError('simulated unavailable exporter')
        self.traces.append(copy.deepcopy(trace))


class Trace:
    def __init__(self,seed,sampled=True,exporter=None,max_spans=64):
        if type(max_spans) is not int or max_spans<1:raise ValueError('span cap')
        self.trace_id=hashlib.sha256(('fixture:'+seed).encode()).hexdigest()[:32]
        self.clock=VirtualClock();self.sampled=sampled;self.exporter=exporter or MemoryExporter()
        self.max_spans=max_spans;self.spans=[];self.stack=[];self.sequence=0
        self.attributes_dropped=0;self.spans_dropped=0;self.export_failures=0

    @contextmanager
    def span(self,name,attributes=None,links=()):
        if name not in NAMES:raise ValueError('span name')
        if any(not isinstance(x,str) or not re.fullmatch('[0-9a-f]{32}',x) for x in links):
            raise ValueError('link')
        attrs,dropped=safe_attributes(attributes or {})
        self.attributes_dropped+=dropped;self.sequence+=1
        row=dict(trace_id=self.trace_id,span_id=f'{self.sequence:016x}',
            parent_id=self.stack[-1] if self.stack else None,name=name,
            start_ms=self.clock.now,end_ms=None,status='ok',attributes=attrs,links=list(links))
        # Bound retained spans even for unsampled traces; no raw exception message.
        retain=len(self.spans)<self.max_spans
        if retain:self.spans.append(row)
        else:self.spans_dropped+=1
        self.stack.append(row['span_id'])
        try:yield row
        except BaseException:
            row['status']='error';raise
        finally:
            row['end_ms']=self.clock.now;self.stack.pop()

    def finish(self):
        if self.stack:raise ValueError('open span')
        if self.sampled:
            try:self.exporter.export({'trace_id':self.trace_id,'spans':self.spans,
                 'attributes_dropped':self.attributes_dropped,'spans_dropped':self.spans_dropped})
            except Exception:self.export_failures+=1


class Probe:
    def __init__(self,target,trace,methods):self.target=target;self.trace=trace;self.methods=methods
    def __getattr__(self,name):
        fn=getattr(self.target,name)
        if name not in self.methods:return fn
        stage,delay=self.methods[name]
        def observed(*args,**kwargs):
            with self.trace.span(stage):
                try:return fn(*args,**kwargs)
                finally:self.trace.clock.advance(delay)
        return observed


class ModelProbe:
    def __init__(self,target,trace):self.target=target;self.trace=trace;self.started=0
    def call(self,model,saved,clock):
        self.started+=1;start=clock.now
        with self.trace.span('model.call',{'model':model.name}):
            try:return self.target.call(model,saved,clock)
            finally:self.trace.clock.advance(clock.now-start)


def observe(store,actor,cache,ledger,gate,task,language='pt-BR',release='r1',
            queue_ms=0,sampled=True,exporter=None,adapter=None,eligible=True,
            assessed=True,source_ms=3,**kwargs):
    # Caller supplies an internal fixture task ID; it is never an attribute.
    if release not in LABELS['release'] or language not in LABELS['language']:
        raise ValueError('labels')
    t=Trace(task+':'+language,sampled,exporter)
    model=ModelProbe(adapter or SimulatedModels(),t)
    with t.span('request',{'language':language,'release':release}):
        with t.span('queue.wait'):t.clock.advance(queue_ms)
        result=execute(
            Probe(store,t,{'prepare':('source.read',source_ms)}),actor,
            Probe(cache,t,{'get':('cache.lookup',2),'put':('cache.write',1)}),
            Probe(ledger,t,{'reserve':('ledger.reserve',1),'settle':('ledger.settle',1),
                            'uncertain':('ledger.uncertain',1)}),
            Probe(gate,t,{'enter':('gate.enter',1)}),task,language,adapter=model,**kwargs)
        if model.started and result['reason']!='cost_unknown':
            with t.span('finalize'):t.clock.advance(20)
    quality='unknown'
    if result['state']=='full' and assessed:
        saved=snapshot(store,actor,kwargs.get('documents',('manual-a','manual-b')),language)
        quality='pass' if cached_valid(result['payload'],saved) else 'fail'
    t.finish()
    row=dict(observation_id=t.trace_id,language=language,release=release,
        eligible=eligible,state=result['state'],quality=quality,cache_hit=result['cache_hit'],
        duration_ms=t.clock.now,queue_ms=queue_ms,processing_ms=t.clock.now-queue_ms,
        calls_started=model.started,settled_units=result['task_units'],held_units=result['held_units'],
        correct_denial=not eligible and result['state']=='abstain' and result['reason']=='access',
        export_failures=t.export_failures,sampled=sampled)
    return row,t


class Measurements:
    """Small offline collector: all rows, independently of trace sampling."""
    def __init__(self):self.rows={}
    def add(self,row):
        key=row['observation_id']
        if key in self.rows:
            if self.rows[key]!=row:raise ValueError('conflicting observation')
            return False
        self.rows[key]=copy.deepcopy(row);return True
    def summary(self,deadline_ms=150):
        rows=list(self.rows.values());eligible=[r for r in rows if r['eligible']]
        good=sum(r['state']=='full' and r['quality']=='pass' and r['duration_ms']<=deadline_ms for r in eligible)
        full=sum(r['state']=='full' for r in rows)
        durations=[r['duration_ms'] for r in rows]
        costs=sum(r['settled_units'] for r in rows)
        return dict(requests=len(rows),eligible=len(eligible),good=good,
            bad=len(eligible)-good,full=full,correct_denials=sum(r['correct_denial'] for r in rows),
            unassessed_full=sum(r['state']=='full' and r['quality']=='unknown' for r in rows),
            p50_ms=percentile(durations,.5),p95_ms=percentile(durations,.95),
            eligible_p95_ms=percentile([r['duration_ms'] for r in eligible],.95),
            processing_p95_ms=percentile([r['processing_ms'] for r in eligible],.95),
            histogram=histogram(durations),calls_started=sum(r['calls_started'] for r in rows),
            settled_units=costs,held_units=sum(r['held_units'] for r in rows),
            units_per_full=round(costs/full,3) if full else None,
            burn=burn_rate(len(eligible)-good,len(eligible)),
            export_failures=sum(r['export_failures'] for r in rows))


def stage_totals(trace):
    totals={}
    for s in trace.spans:
        if s['name']=='request':continue
        totals[s['name']]=totals.get(s['name'],0)+s['end_ms']-s['start_ms']
    return totals
