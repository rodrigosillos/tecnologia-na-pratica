"""Reproducible scenario matrix using virtual time; HTTP tested separately."""
import argparse
from dataclasses import asdict
import json
from pathlib import Path
from adapters import JsonRepository, ManualClock, ROOT, StubGenerator
from contracts import Principal, Query
from http_api import status_for
from service import AnswerService
from settings import Settings
from solutions import exercise5, exercise6


def evaluate():
    rows=[]
    cases=[('good','returns'),('good','sunday'),('good','payroll'),
           ('good','emergency'),('malformed','returns'),('unsupported','returns'),
           ('incomplete','returns'),('refused','returns'),('timeout','returns'),
           ('unavailable','returns'),('unknown_usage','returns'),('expensive','returns')]
    for mode,topic in cases:
        svc=AnswerService(JsonRepository(ROOT/'documents.json'),
                          StubGenerator(mode),ManualClock(),Settings())
        result=svc.answer(Principal('acme','operator'),Query(topic))
        rows.append({'mode':mode,'topic':topic,'http_status':status_for(result),
                     **asdict(result)})
    return {'measurement_kind':'controlled_stubs_virtual_time_not_provider_benchmark',
            'rows':rows,'exercises':{'5':exercise5(),'6':exercise6()}}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',type=Path,default=ROOT/'results/experiments.json')
    a=p.parse_args();result=evaluate()
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'scenarios':len(result['rows']),'exercises':[5,6]},indent=2))
