from pathlib import Path
import json
from store import Actor, Conflict, Copilot, Store

ALICE = Actor('acme', 'alice')
BOB = Actor('zen', 'bob')

def seeded(path=':memory:'):
    s = Store(path)
    s.principal('acme', 'alice', 'staff')
    s.principal('acme', 'ana', 'admin')
    s.principal('zen', 'bob', 'staff')
    s.publish('acme', 'returns', 'Prazo: 30 dias.', 'Window: 30 days.',
              'urn:acme:returns:v1', ['staff', 'admin'], 0, 'a-1')
    s.publish('zen', 'returns', 'Prazo: 7 dias.', 'Window: 7 days.',
              'urn:zen:returns:v1', ['staff'], 0, 'z-1')
    s.publish('acme', 'payroll', 'Fechamento: dia 20.', 'Cutoff: day 20.',
              'urn:acme:payroll:v1', ['admin'], 0, 'p-1')
    s.drain()
    return s

def new_version(s, fail=False):
    return s.publish('acme', 'returns', 'Prazo: 45 dias.', 'Window: 45 days.',
                     'urn:acme:returns:v2', ['staff', 'admin'], 1, 'a-2', fail)

def run_scenarios():
    rows = []
    def record(name, ok, observed):
        rows.append({'scenario':name,'passed':bool(ok),'observed':observed})
    s = seeded()
    try:
        c = Copilot(s)
        a = c.answer(ALICE, 'returns')
        b = c.answer(BOB, 'returns')
        record('tenant_isolation', a['answer']=='Prazo: 30 dias.' and
               b['answer']=='Prazo: 7 dias.', [a['answer'],b['answer']])
        forged = c.answer(Actor('zen','alice'), 'returns')
        record('unknown_membership', forged['status']=='unavailable', forged['status'])
        denied = c.answer(ALICE, 'payroll')
        record('role_denied', denied['answer'] is None, denied['status'])
        hit = c.answer(ALICE, 'returns')
        record('authorized_cache_hit', hit['cached'], hit['cached'])
        english = c.answer(ALICE, 'returns', 'en-US')
        record('language_separated', english['answer']=='Window: 30 days.' and
               not english['cached'], english['answer'])
        new_version(s)
        lag = c.answer(ALICE, 'returns')
        record('index_lag_blocks', lag['status']=='unavailable', lag['status'])
        s.drain()
        fresh = c.answer(ALICE, 'returns')
        record('published_version', fresh['answer']=='Prazo: 45 dias.' and
               fresh['citations'][0]['version']==2, fresh['citations'][0]['version'])
        s.process(1, replay=True)
        snap = s.prepare(ALICE, 'returns', 'pt-BR')
        record('old_event_no_rollback', snap.version==2, snap.version)
        revoked = c.answer(ALICE, 'returns', between=lambda:s.set_acl('acme','returns',['admin']))
        record('revoke_before_release', revoked['status']=='unavailable', revoked['status'])
        after = c.answer(ALICE, 'returns')
        record('cached_answer_after_revoke', after['answer'] is None, after['status'])
        s.delete('acme', 'returns', day=10, retention_days=2)
        s.process(1, replay=True)
        hidden = s.prepare(Actor('acme','ana'), 'returns', 'pt-BR')
        record('late_event_after_delete', hidden is None and s.db.execute(
            "SELECT count(*) FROM projection WHERE tenant='acme' AND doc_id='returns'"
        ).fetchone()[0]==0, 'unavailable')
        early, due = s.purge(11), s.purge(12)
        c.cache.clear()  # Local cache purge is explicit; SQL purge cannot erase RAM.
        record('retention_deadline', (early,due)==(0,1), [early,due])
    finally:
        s.close()
    return {'kind':'offline deterministic lifecycle scenarios','scenarios':rows,
            'passed':sum(r['passed'] for r in rows),'total':len(rows)}

if __name__ == '__main__':
    result = run_scenarios()
    folder = Path(__file__).with_name('results');folder.mkdir(exist_ok=True)
    (folder/'scenarios.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))
