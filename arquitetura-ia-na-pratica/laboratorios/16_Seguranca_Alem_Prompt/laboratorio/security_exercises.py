from security_scenarios import run_case
from security_gate import render_quote


def exercise31():
    cases=('role_spoof','proposal_denied',
           'proposal_pending','approval_forgery')
    rows=[run_case(name) for name in cases]
    assert [r['status'] for r in rows]==[
        'blocked','blocked','pending','blocked']
    assert sum(r['intents'] for r in rows)==1
    assert sum(r['effects'] for r in rows)==0
    return {'states':[r['status'] for r in rows],
            'pending_intents':1,'effects':0}


def exercise32():
    bad='<img src="https://sink.invalid/">'
    encoded=render_quote(bad)
    poison=run_case('poisoned_fact')
    conflict=run_case('conflict')
    assert '<img' not in encoded
    assert poison['status']=='answered'
    assert conflict['status']=='blocked'
    return {'markup_encoded':True,
            'poisoned_fact_accepted':True,
            'conflicting_fact_blocked':True,
            'truth_verified':False}
