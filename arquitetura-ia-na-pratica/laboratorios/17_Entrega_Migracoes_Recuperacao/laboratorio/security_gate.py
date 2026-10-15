"""Chapter 16: deterministic host boundary; no model or network client."""
from dataclasses import dataclass
import html,json,re
from control import unique_object
from retrieval import PATTERNS
from actions import Denied

POLICY='quote-boundary-v1'
LANGUAGES=('pt-BR','en-US')
FIELDS={'quote':{'kind','start','stop'},
        'abstain':{'kind'},'propose':{'kind','topic'}}


def parse_candidate(raw):
    if type(raw) is not str:
        raise ValueError('schema')
    if len(raw.encode('utf-8'))>768:
        raise ValueError('size')
    obj=json.loads(raw,object_pairs_hook=unique_object)
    if type(obj) is not dict:
        raise ValueError('schema')
    kind=obj.get('kind')
    if type(kind) is not str or kind not in FIELDS:
        raise ValueError('schema')
    if set(obj)!=FIELDS[kind]:
        raise ValueError('schema')
    if kind=='quote':
        a,b=obj['start'],obj['stop']
        if type(a) is not int or type(b) is not int:
            raise ValueError('schema')
        if not 0<=a<b<=4096:
            raise ValueError('bounds')
    if kind=='propose' and obj['topic'] not in (
            'returns','shipping'):
        raise ValueError('schema')
    return obj


def render_quote(text):
    return '<p>'+html.escape(text,quote=True)+'</p>'


def pattern(topic,language):
    return PATTERNS[language][topic]


@dataclass(frozen=True)
class Scope:
    actor:object
    document:str='manual-a'
    topic:str='returns'
    language:str='pt-BR'
    allow_proposal:bool=False

    def __post_init__(self):
        if self.language not in LANGUAGES:
            raise ValueError('language')
        if self.topic not in ('returns','shipping'):
            raise ValueError('topic')
        if type(self.allow_proposal) is not bool:
            raise ValueError('capability')


class Boundary:
    """Trusted host object, never exposed to an untrusted Python plugin."""
    def __init__(self,store,scope,service=None):
        self.store,self.scope,self.service=store,scope,service
        self.used=False;self.events=[];self.snapshot=None
        s=store.prepare(scope.actor,scope.document,scope.language)
        if s is None:
            raise Denied('source_access')
        if len(s.body)>4096:
            raise Denied('source_size')
        self.snapshot=s

    def context(self):
        # Labels guide a future model; only host checks enforce authority.
        if not self.store.still_current(self.snapshot):
            raise Denied('stale_or_revoked')
        return json.dumps({'task':'select an exact fact span or abstain',
            'topic':self.scope.topic,'language':self.scope.language,
            'source':{'trust':'untrusted_content',
                      'text':self.snapshot.body}},ensure_ascii=False)

    def finish(self,status,reason,**details):
        self.events.append({'policy':POLICY,'status':status,'reason':reason})
        return {'status':status,'reason':reason,**details}

    def accept(self,raw):
        if self.used:
            return self.finish('blocked','consumed')
        self.used=True
        try:obj=parse_candidate(raw)
        except (ValueError,TypeError,UnicodeError,RecursionError):
            return self.finish('blocked','invalid_candidate')
        if not self.store.still_current(self.snapshot):
            return self.finish('blocked','stale_or_revoked')
        if obj['kind']=='abstain':
            return self.finish('abstained','model_abstained')
        if obj['kind']=='propose':
            return self.propose(obj)
        matches=list(re.finditer(pattern(self.scope.topic,
                                  self.scope.language),self.snapshot.body))
        if len({m.group(1) for m in matches})!=1:
            return self.finish('blocked','missing_or_conflicting_fact')
        selected=next((m for m in matches
                       if m.span()==(obj['start'],obj['stop'])),None)
        if selected is None:
            return self.finish('blocked','unsupported_span')
        quote=selected.group(0)
        return self.finish('answered','exact_source_fact',text=quote,
            html=render_quote(quote),citation={'document':self.scope.document,
                'version':self.snapshot.version,'digest':self.snapshot.digest,
                'start':selected.start(),'stop':selected.end()})

    def propose(self,obj):
        if (not self.scope.allow_proposal or self.service is None
                or self.scope.document!='manual-a'
                or obj['topic']!=self.scope.topic):
            return self.finish('blocked','capability')
        draft=json.dumps({'tool':'prepare_task','project':'ops',
                          'topic':self.scope.topic})
        try:
            id=self.service.propose(self.scope.actor,draft,
                                    language=self.scope.language)
        except Denied:
            return self.finish('blocked','action_policy')
        return self.finish('pending','human_review_required',intent_id=id)


def fact_candidate(boundary):
    """Fixture helper, not a real LLM. Offsets are Python Unicode indexes."""
    s=boundary.scope
    match=re.search(pattern(s.topic,s.language),boundary.snapshot.body)
    if match is None:return json.dumps({'kind':'abstain'})
    return json.dumps({'kind':'quote','start':match.start(),'stop':match.end()})
