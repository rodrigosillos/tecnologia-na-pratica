"""Systems receive requests only, never evaluation labels. No network calls."""
from dataclasses import dataclass, replace
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'app'))
from adapters import JsonRepository, ManualClock, StubGenerator
from contracts import Outcome, Principal, Query
from service import AnswerService
from settings import Settings


@dataclass(frozen=True)
class Request:
    tenant: str
    role: str
    topic: str
    language: str


class TimedRepository:
    def __init__(self, inner, clock):
        self.inner, self.clock=inner,clock

    def search(self, principal, topic, snapshot):
        self.clock.advance(40)
        return self.inner.search(principal,topic,snapshot)


class TimedGenerator:
    def __init__(self,clock):self.clock=clock

    def complete(self,query,documents,limits):
        self.clock.advance(860)
        return StubGenerator().complete(query,documents,limits)


class System:
    MODES=('baseline','fast_unsafe','refuse_all','missing_meter')

    def __init__(self, mode):
        if mode not in self.MODES:raise ValueError('unknown system')
        self.mode=mode
        self.repo=JsonRepository(ROOT/'app/documents.json')

    def run(self, request:Request):
        if self.mode=='refuse_all':
            return Outcome('abstain',None,None,'insufficient_evidence',0,20)
        if self.mode=='fast_unsafe':
            # Deliberately broken optimization: cache key is only topic.
            docs=[d for d in self.repo.documents if d.topic==request.topic]
            if not docs:
                return Outcome('abstain',None,None,'insufficient_evidence',0,20)
            doc=docs[0]
            text=doc.text_pt if request.language=='pt-BR' else doc.text_en
            return Outcome('answer',text,doc.id,None,200,120)
        clock=ManualClock()
        service=AnswerService(TimedRepository(self.repo,clock),
            TimedGenerator(clock),clock,Settings())
        result=service.answer(Principal(request.tenant,request.role),
                              Query(request.topic,request.language))
        # Evaluation-only telemetry fault, not the behavior of chapter 3.
        if self.mode=='missing_meter' and result.status=='answer':
            result=replace(result,cost_microusd=None)
        return result
