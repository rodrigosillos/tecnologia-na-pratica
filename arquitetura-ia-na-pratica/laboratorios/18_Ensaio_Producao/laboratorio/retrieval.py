"""Exact local retrieval over authorized Chapter 6 generations.
Concept vectors are hand-built teaching features, not learned embeddings.
"""
from collections import Counter,defaultdict
from dataclasses import dataclass
from hashlib import sha256
import json,math,re,unicodedata

VECTOR_VERSION='concepts-v1'
TOPICS=('returns','shipping','reset','backup','rate','support')
ALIASES=(
 {'devolucao','devolver','arrependimento','trocar','returns','refund','exchange'},
 {'postagem','envio','despacho','shipping','dispatch','shipment'},
 {'senha','redefinicao','esqueci','password','forgot','reset'},
 {'backup','backups','restauracao','copia','restore','retention'},
 {'429','limite','quota','rate','retry','throttling'},
 {'suporte','atendimento','support','helpdesk'},
)
STOP=set('a o os as de da do das dos e em no na um uma qual quanto quantos '
         'que para por posso meu minha the a an of for to in is are what '
         'how can i my do does'.split())
TIME=set('prazo tempo dias dia minutos segundos horas validade quando '
         'window long many days minutes seconds hours when valid wait'.split())
IDS={f'pol-{name}-01':topic for name,topic in zip(('ret','ship','auth','bak','api','sup'),TOPICS)}

def tokens(text):
    value=unicodedata.normalize('NFKD',text.casefold())
    value=''.join(c for c in value if not unicodedata.combining(c))
    return [w for w in re.findall(r'[a-z0-9]+(?:-[a-z0-9]+)*',value) if w not in STOP]

def concept_vector(text):
    words=set(tokens(text))
    return tuple(float(bool(words & group)) for group in ALIASES)

def cosine(a,b):
    if len(a)!=len(b):raise ValueError('dimension mismatch')
    if not all(math.isfinite(x) for x in (*a,*b)):raise ValueError('nonfinite vector')
    denominator=math.sqrt(sum(x*x for x in a)*sum(x*x for x in b))
    return sum(x*y for x,y in zip(a,b))/denominator if denominator else 0.0

def bm25(query, texts, k1=1.2, b=0.75):
    if k1<=0 or not 0<=b<=1:raise ValueError('invalid BM25 settings')
    bags=[Counter(tokens(text)) for text in texts]
    n=len(bags)
    average=sum(sum(bag.values()) for bag in bags)/n if n else 0
    if not average:return [0.0]*n
    result=[0.0]*n
    for term in set(tokens(query)):
        df=sum(term in bag for bag in bags)
        idf=math.log(1+(n-df+0.5)/(df+0.5))
        for i,bag in enumerate(bags):
            tf=bag[term]
            length=sum(bag.values())
            denominator=tf+k1*(1-b+b*length/average)
            result[i]+=idf*tf*(k1+1)/denominator
    return result

def reciprocal_rank_fusion(rankings, k=60):
    if k<=0:raise ValueError('positive fusion constant required')
    scores=defaultdict(float)
    for ranking in rankings:
        unique=list(dict.fromkeys(ranking))
        for rank,key in enumerate(unique,1):
            scores[key]+=1/(k+rank)
    return sorted(scores.items(),
                  key=lambda pair:(-pair[1],pair[0]))

@dataclass(frozen=True)
class Evidence:
    snapshot: object
    job: str
    chunk: str
    ordinal: int
    start: int
    stop: int
    text: str
    digest: str

def valid_evidence(store,evidence):
    e=evidence;s=e.snapshot
    if not store.still_current(s):return False
    row=store.db.execute('''SELECT c.* FROM chunks c JOIN heads h
      ON h.job_id=c.job_id WHERE h.tenant=? AND h.doc_id=?
      AND h.version=? AND c.chunk_id=?''',
      (s.tenant,s.document,s.version,e.chunk)).fetchone()
    if row is None:return False
    expected=(e.job,s.language,e.ordinal,e.start,e.stop,e.text,e.digest)
    actual=tuple(row[k] for k in ('job_id','language','ordinal','start','stop','body','digest'))
    return (actual==expected and 0<=e.start<e.stop<=len(s.body)
            and s.body[e.start:e.stop]==e.text
            and sha256(e.text.encode()).hexdigest()==e.digest)

def collect(store,actor,language):
    if language not in ('pt-BR','en-US'):raise ValueError('unsupported language')
    docs=[r[0] for r in store.db.execute(
        'SELECT doc_id FROM documents WHERE tenant=? ORDER BY doc_id',(actor.tenant,))]
    result=[]
    for doc in docs:
        snapshot=store.prepare(actor,doc,language)
        if snapshot is None:continue
        for row in store.visible_chunks(actor,doc,language):
            e=Evidence(snapshot,row['job_id'],row['chunk_id'],row['ordinal'],
                       row['start'],row['stop'],row['body'],row['digest'])
            if valid_evidence(store,e):result.append(e)
    return result

def rank(query,evidence,mode='hybrid',depth=4):
    if mode not in ('lexical','vector','hybrid'):raise ValueError('unknown mode')
    if type(depth) is not int or depth<1:raise ValueError('positive depth required')
    ids=[e.chunk for e in evidence]
    lexical=bm25(query,[e.text for e in evidence])
    qv=concept_vector(query)
    vector=[cosine(qv,concept_vector(e.text)) for e in evidence]
    def order(values):
        pairs=[(key,value) for key,value in zip(ids,values) if value>0]
        return [key for key,value in sorted(pairs,key=lambda p:(-p[1],p[0]))[:depth]]
    left,right=order(lexical),order(vector)
    chosen=left if mode=='lexical' else right if mode=='vector' else [key for key,_ in reciprocal_rank_fusion([left,right])]
    lookup={e.chunk:e for e in evidence}
    return [lookup[key] for key in chosen]

def serialize_context(evidence):
    return json.dumps([{'document':e.snapshot.document,'version':e.snapshot.version,
                       'chunk':e.chunk,'source':e.snapshot.source,'text':e.text}
                      for e in evidence],ensure_ascii=False,separators=(',',':'))

def select_context(ranked,budget=1100,limit=3):
    if type(budget) is not int or budget<2 or type(limit) is not int or limit<1:
        raise ValueError('invalid context limits')
    selected=[];seen=set()
    for e in ranked:
        key=(e.snapshot.tenant,e.snapshot.document)
        if key in seen:continue
        if len(serialize_context(selected+[e]))>budget:continue
        selected.append(e);seen.add(key)
        if len(selected)==limit:break
    return selected

def classify(query):
    words=set(tokens(query))
    topics={TOPICS[i] for i,g in enumerate(ALIASES) if words & g}
    topics|={IDS[w] for w in words if w in IDS}
    if len(topics)>1:return 'clarify',None
    if not topics:return ('clarify' if words and words<=TIME else 'abstain'),None
    allowed=set().union(*ALIASES)|TIME|set(IDS)
    if words-allowed:return 'abstain',None
    return 'ready',next(iter(topics))

PATTERNS={
 'pt-BR':{
  'returns':r'Devolução: prazo de (\d+) dias\.',
  'shipping':r'Postagem: despacho em (\d+) dias\.',
  'reset':r'Redefinição de senha: link válido por (\d+) minutos\.',
  'backup':r'Backup: retenção de (\d+) dias\.',
  'rate':r'Erro 429: aguarde (\d+) segundos antes de repetir\.',
  'support':r'Suporte: resposta em até (\d+) horas\.'},
 'en-US':{
  'returns':r'Returns: window of (\d+) days\.',
  'shipping':r'Shipping: dispatch in (\d+) days\.',
  'reset':r'Password reset: link valid for (\d+) minutes\.',
  'backup':r'Backup: retention of (\d+) days\.',
  'rate':r'Error 429: wait (\d+) seconds before retry\.',
  'support':r'Support: response within (\d+) hours\.'}}

def extract_claim(evidence,topic,language):
    found=[]
    for e in evidence:
        for match in re.finditer(PATTERNS[language][topic],e.text):
            found.append((e,match))
    if not found:return None,'no_supported_claim'
    if len({m.group(1) for _,m in found})>1:return None,'conflicting_claims'
    e,match=found[0]
    return {'text':match.group(0),'document':e.snapshot.document,
            'version':e.snapshot.version,'chunk':e.chunk,'digest':e.digest,
            'source':e.snapshot.source,'start':e.start+match.start(),
            'stop':e.start+match.end()},None

def answer(store,actor,query,language='pt-BR',mode='hybrid',
           budget=1100,between=None):
    if not isinstance(query,str) or not 0<len(query)<=400:
        raise ValueError('query must contain 1..400 characters')
    if language not in PATTERNS:raise ValueError('unsupported language')
    def empty(status,reason):
        return dict(status=status,text=None,citations=[],reason=reason)
    state,topic=classify(query)
    if state!='ready':return empty(state,'unsupported_or_ambiguous_query')
    ranked=rank(query,collect(store,actor,language),mode)
    # A conflict seen in candidates must not be hidden by context budgeting.
    _,reason=extract_claim(ranked,topic,language)
    if reason=='conflicting_claims':return empty('abstain',reason)
    context=select_context(ranked,budget)
    if not all(valid_evidence(store,e) for e in context):
        return empty('abstain','state_changed')
    claim,reason=extract_claim(context,topic,language)
    if claim is None:return empty('abstain',reason)
    if between:between()
    if not all(valid_evidence(store,e) for e in context):
        return empty('abstain','state_changed')
    return dict(status='answer',text=claim['text'],citations=[claim],reason=None)

def verify_citation(store,actor,response,language):
    if response['status']!='answer':
        return response['text'] is None and response['citations']==[]
    if len(response['citations'])!=1:return False
    cite=response['citations'][0]
    snapshot=store.prepare(actor,cite['document'],language)
    if snapshot is None:return False
    evidence=collect(store,actor,language)
    e=next((e for e in evidence if e.chunk==cite['chunk']),None)
    return (e is not None and e.snapshot==snapshot
            and cite['version']==snapshot.version
            and cite['source']==snapshot.source
            and cite['digest']==e.digest
            and e.start<=cite['start']<cite['stop']<=e.stop
            and snapshot.body[cite['start']:cite['stop']]
                ==cite['text']==response['text'])
