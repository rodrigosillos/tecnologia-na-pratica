import json
from scenarios import ALICE, new_version, seeded
from store import Copilot

def exercise9():
    s = seeded()
    try:
        before = s.db.total_changes
        try:
            new_version(s, fail=True)
        except RuntimeError:
            pass
        # total_changes is not a committed-state audit.
        snap = s.prepare(ALICE, 'returns', 'pt-BR')
        assert snap.version == 1
        assert s.db.execute(
            "SELECT count(*) FROM outbox WHERE done=0"
        ).fetchone()[0] == 0
        v = new_version(s)
        assert new_version(s) == v == 2
        assert s.prepare(ALICE, 'returns', 'pt-BR') is None
        s.drain()
        assert s.prepare(ALICE, 'returns', 'pt-BR').version == 2
        counted_activity = s.db.total_changes > before
        return {'version':v, 'rollback_preserved_v1':True,
                'retry_idempotent':True,
                'total_changes_not_commit_count':counted_activity}
    finally:
        s.close()

def exercise10():
    s = seeded()
    try:
        c = Copilot(s)
        assert c.answer(ALICE, 'returns')['status'] == 'answer'
        def revoke():
            s.set_acl('acme', 'returns', ['admin'])
        result = c.answer(ALICE, 'returns', between=revoke)
        assert result['status'] == 'unavailable'
        assert c.answer(ALICE, 'returns')['answer'] is None
        s.delete('acme', 'returns', 10, 2)
        s.process(1, replay=True)
        assert s.purge(11) == 0
        assert s.purge(12) == 1
        c.cache.clear()
        return {'blocked_after_revoke':True,
                'purged_documents':1, 'cache_entries':len(c.cache)}
    finally:
        s.close()

if __name__ == '__main__':
    print(json.dumps({'exercise9':exercise9(),'exercise10':exercise10()},indent=2))
