import json
from pathlib import Path
from threading import Event
from fixtures import seeded, ALICE
from scenarios import request, wire as scenario_wire
from client import consume, fragments
from contract import ContractError
# English requests for the chapter 8 exercises.
def wire(store, **options):
    req = request(['Returns window?', 'Shipping days?'], 'en-US')
    return scenario_wire(store, req, **options)

def exercise15():
    store = seeded()
    try:
        frames = wire(store)
        good = consume(fragments(b''.join(frames), 1),
                       'demo-08', ['q1', 'q2'])
        assert good.result['outcome'] == 'complete'
        for damaged in (frames[:-1], frames[:2] + frames[1:]):
            try:
                consume(damaged, 'demo-08', ['q1', 'q2'])
            except ContractError:
                continue
            raise AssertionError('invalid stream accepted')
        return dict(valid='complete', truncated='rejected',
                    duplicate='rejected')
    finally:
        store.close()

def exercise16():
    store = seeded()
    token = Event()
    try:
        def revoke():
            store.set_acl('acme', 'returns', ['admin'])
        partial = consume(wire(store, before_release=revoke),
                          'demo-08', ['q1', 'q2'])
        assert partial.result['outcome'] == 'partial'
        a, b = partial.result['items']
        assert a['status'] == 'abstain'
        assert a['citations'] == []
        assert b['status'] == 'answer'
        cancelled = consume(wire(store, cancel=token,
                            before_release=token.set),
                            'demo-08', ['q1', 'q2'])
        assert cancelled.state == 'cancelled'
        assert cancelled.result is None
        return dict(revoked_item=a['status'],
                    retained_item=b['status'],
                    cancelled=cancelled.state)
    finally:
        store.close()

if __name__ == '__main__':
    data={'exercise15':exercise15(),'exercise16':exercise16()}
    out=Path('results');out.mkdir(exist_ok=True)
    (out/'solutions_en.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
    print(json.dumps(data,indent=2))
