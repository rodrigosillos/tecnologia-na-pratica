from pathlib import Path
from tempfile import TemporaryDirectory
import json
from scenarios import seeded, submit, stage, ALICE
from pipeline import Pipeline, LostLease, Copilot

def exercise11():
    with TemporaryDirectory(dir=Path(__file__).parent) as temp:
        path = str(Path(temp) / 'resume.sqlite')
        s = seeded(path)
        job = submit(s)
        first = s.claim(job, 'worker-a', 0)
        s.prepare_job(first, 1)
        s.write_batch(first, 2)
        checkpoint = s.job(job)['cursor']
        s.close()  # Lost response after a committed batch.
        s = Pipeline(path)
        try:
            second = s.claim(job, 'worker-b', 10)
            stage(s, second, 11)
            version = s.activate(second, 12)
            s.drain()
            rows = s.db.execute(
                'SELECT chunk_id FROM chunks WHERE job_id=?',
                (job,)).fetchall()
            duplicates = len(rows) - len(set(r[0] for r in rows))
            assert checkpoint == 2 and duplicates == 0
            assert len(rows) == s.job(job)['total'] == 6
            assert version == 2
            assert len(s.visible_chunks(ALICE, 'returns')) == 3
            return dict(checkpoint=checkpoint, chunks=len(rows),
                        duplicates=duplicates, version=version)
        finally:
            s.close()

def exercise12():
    s = seeded()
    try:
        job = submit(s)
        first = s.claim(job, 'worker-a', 0)
        s.prepare_job(first, 1)
        s.write_batch(first, 2)
        second = s.claim(job, 'worker-b', 10)
        blocked = False
        try:
            s.write_batch(first, 11)
        except LostLease:
            blocked = True
        stage(s, second, 11)
        s.set_acl('acme', 'returns', ['admin'])
        version = s.activate(second, 12)
        state = s.job(job)['state']
        answer = Copilot(s).answer(ALICE, 'returns')
        assert blocked and version is None
        assert state == 'obsolete'
        assert answer['status'] == 'unavailable'
        active = s.db.execute(
            "SELECT active_version FROM documents "
            "WHERE tenant='acme' AND doc_id='returns'").fetchone()[0]
        assert active == 1
        return dict(stale_worker_blocked=blocked, state=state,
                    active_version=active, answer=answer['status'])
    finally:
        s.close()

if __name__=='__main__':
    result={'exercise11':exercise11(),'exercise12':exercise12()}
    folder=Path(__file__).with_name('results');folder.mkdir(exist_ok=True)
    (folder/'solutions.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))
