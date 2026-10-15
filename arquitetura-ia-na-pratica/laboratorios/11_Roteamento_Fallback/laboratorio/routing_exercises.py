from pathlib import Path
import json
from fixtures import ALICE
from job_worker import manuals
from routing import RoutePolicy, Reply, SimulatedModels, route


def exercise21():
    store=manuals()
    try:
        adapter=SimulatedModels({'compact':Reply('transient')})
        report=route(store,ALICE,adapter=adapter,
                     policy=RoutePolicy(max_units=89))
        assert adapter.calls==['compact']
        assert report['state']=='abstain'
        assert report['charged_units']==20
        assert any(t.get('reason')=='privacy'
                   for t in report['trace'])
        return dict(state=report['state'],calls=adapter.calls,
                    units=report['charged_units'])
    finally:store.close()


def exercise22():
    store=manuals()
    try:
        adapter=SimulatedModels({'compact':Reply('partial')})
        report=route(store,ALICE,adapter=adapter,
                     policy=RoutePolicy(max_units=20))
        assert report['state']=='partial'
        assert report['missing']==['shipping']
        assert report['rows'][0]['delta']==-15
        return dict(state=report['state'],missing=report['missing'],
                    delta=report['rows'][0]['delta'],
                    units=report['charged_units'])
    finally:store.close()


if __name__=='__main__':
    report=dict(exercise21=exercise21(),exercise22=exercise22())
    out=Path('results');out.mkdir(exist_ok=True)
    (out/'exercises.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))
