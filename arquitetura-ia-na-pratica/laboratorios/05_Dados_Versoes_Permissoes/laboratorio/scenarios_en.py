"""English chapter 5 scenarios; bilingual fixtures remain unchanged."""
import json
from scenarios import ALICE, BOB, seeded, new_version
from store import Actor, Copilot

def run_scenarios():
    rows = []

    def record(name, ok, observed):
        rows.append({'scenario': name, 'passed': bool(ok), 'observed': observed})
    s = seeded()
    try:
        c = Copilot(s)
        a = c.answer(ALICE, 'returns', 'en-US')
        b = c.answer(BOB, 'returns', 'en-US')
        record('tenant_isolation', a['answer'] == 'Window: 30 days.' and b['answer'] == 'Window: 7 days.', [a['answer'], b['answer']])
        forged = c.answer(Actor('zen', 'alice'), 'returns', 'en-US')
        record('unknown_membership', forged['status'] == 'unavailable', forged['status'])
        denied = c.answer(ALICE, 'payroll', 'en-US')
        record('role_denied', denied['answer'] is None, denied['status'])
        hit = c.answer(ALICE, 'returns', 'en-US')
        record('authorized_cache_hit', hit['cached'], hit['cached'])
        other = c.answer(ALICE, 'returns', 'pt-BR')
        separate = other['answer'] == 'Prazo: 30 dias.' and (not other['cached'])
        record('language_separated', separate, separate)
        new_version(s)
        lag = c.answer(ALICE, 'returns', 'en-US')
        record('index_lag_blocks', lag['status'] == 'unavailable', lag['status'])
        s.drain()
        fresh = c.answer(ALICE, 'returns', 'en-US')
        record('published_version', fresh['answer'] == 'Window: 45 days.' and fresh['citations'][0]['version'] == 2, fresh['citations'][0]['version'])
        s.process(1, replay=True)
        snap = s.prepare(ALICE, 'returns', 'en-US')
        record('old_event_no_rollback', snap.version == 2, snap.version)
        revoked = c.answer(ALICE, 'returns', 'en-US', between=lambda: s.set_acl('acme', 'returns', ['admin']))
        record('revoke_before_release', revoked['status'] == 'unavailable', revoked['status'])
        after = c.answer(ALICE, 'returns', 'en-US')
        record('cached_answer_after_revoke', after['answer'] is None, after['status'])
        s.delete('acme', 'returns', day=10, retention_days=2)
        s.process(1, replay=True)
        hidden = s.prepare(Actor('acme', 'ana'), 'returns', 'en-US')
        record('late_event_after_delete', hidden is None and s.db.execute("SELECT count(*) FROM projection WHERE tenant='acme' AND doc_id='returns'").fetchone()[0] == 0, 'unavailable')
        early, due = (s.purge(11), s.purge(12))
        c.cache.clear()
        record('retention_deadline', (early, due) == (0, 1), [early, due])
    finally:
        s.close()
    return {'kind': 'offline deterministic lifecycle scenarios', 'scenarios': rows, 'passed': sum((r['passed'] for r in rows)), 'total': len(rows)}

if __name__ == '__main__':
    from pathlib import Path
    result = run_scenarios()
    out = Path(__file__).with_name('results')
    out.mkdir(exist_ok=True)
    (out/'scenarios_en.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))
