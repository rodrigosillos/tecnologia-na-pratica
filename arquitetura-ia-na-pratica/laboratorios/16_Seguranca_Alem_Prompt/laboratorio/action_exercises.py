from action_scenarios import fixture,approve,DRAFT,REVIEWER
from fixtures import ALICE
from actions import Denied


def exercise29():
    store,service,dest=fixture()
    try:
        first=service.propose(ALICE,DRAFT)
        second=service.propose(ALICE,DRAFT)
        view=service.preview(REVIEWER,first)
        approve(service,first)
        # An approved payload does not approve another intent.
        second_state=service.dispatch(second,dest)
        try:
            service.decide(REVIEWER,second,'0'*64,True)
        except Denied as e:
            mismatch=str(e)
        service.dispatch(first,dest)
        return {'same_payload_hash':view['hash']==
                service.row(second)['hash'],
                'unapproved_state':second_state,
                'wrong_preview':mismatch,
                'effects':dest.count()}
    finally:
        service.close();dest.close();store.close()


def exercise30():
    store,service,dest=fixture()
    try:
        id=service.propose(ALICE,DRAFT)
        approve(service,id)
        before=service.dispatch(id,dest,fault='after')
        service.grant(REVIEWER,'reviewer',False)
        after=service.reconcile(id,dest,now=40,retry=True)
        return {'before':before,'after':after,
                'effects':dest.count(),
                'create_calls':dest.calls,
                'lookups':dest.lookups,
                'reason':service.row(id)['reason']}
    finally:
        service.close();dest.close();store.close()


if __name__=='__main__':
    import json
    print(json.dumps({'exercise29':exercise29(),'exercise30':exercise30()},indent=2))
