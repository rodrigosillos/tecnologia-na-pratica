from cache_cost import (AnswerCache, Ledger, Gate, execute)
from fixtures import ALICE
from job_worker import manuals


def exercise23():
    store=manuals();cache=AnswerCache();ledger=Ledger()
    ledger.configure('acme',200);gate=Gate()
    try:
        first=execute(store,ALICE,cache,ledger,gate,'a')
        second=execute(store,ALICE,cache,ledger,gate,'b',now=1)
        store.set_acl('acme','manual-a',['admin'])
        third=execute(store,ALICE,cache,ledger,gate,'c',now=2)
        return {'states':[r['state'] for r in (first,second,third)],
                'calls':[r['model_calls'] for r in (first,second,third)],
                'spent':ledger.balance('acme')['spent']}
    finally:
        store.close();cache.close();ledger.close()


def exercise24():
    ledger=Ledger();ledger.configure('acme',200)
    try:
        first=ledger.reserve('acme','a','key-a',94)
        second=ledger.reserve('acme','b','key-b',94)
        third=ledger.reserve('acme','c','key-c',94)
        ledger.settle('acme','a',24)
        ledger.uncertain('acme','b')
        before=ledger.balance('acme')
        ledger.settle('acme','b',74)
        ledger.settle('acme','b',74)
        after=ledger.balance('acme')
        return {'admissions':[first,second,third],
                'before':before,'after':after}
    finally:ledger.close()


if __name__=='__main__':
    import json
    from pathlib import Path
    result={'exercise23':exercise23(),'exercise24':exercise24()}
    Path('results').mkdir(exist_ok=True)
    Path('results/exercises.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))
