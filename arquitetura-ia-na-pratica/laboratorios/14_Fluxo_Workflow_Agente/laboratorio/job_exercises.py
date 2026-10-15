import json
from pathlib import Path
from fixtures import ALICE
from async_jobs import Jobs, LocalQueue, Crash, IdempotencyConflict
from resilience import Clock
from job_worker import manuals, payload, work_once, read_job


def exercise19():
    jobs, queue, store = Jobs(), LocalQueue(), manuals()
    try:
        first = jobs.submit(ALICE, 'same-intent', payload(), 0)
        replay = jobs.submit(ALICE, 'same-intent', payload(), 1)
        try:
            jobs.relay(queue, 0, crash_after_publish=True)
        except Crash:
            pass
        jobs.relay(queue, 0)
        before = queue.pending()
        clock = Clock()
        work_once(jobs, queue, store, clock)
        work_once(jobs, queue, store, clock)
        count = jobs.db.execute(
            'SELECT count(*) FROM job_results').fetchone()[0]
        job_count = jobs.db.execute(
            'SELECT count(*) FROM jobs').fetchone()[0]
        assert first['job_id'] == replay['job_id']
        assert before == 2 and count == job_count == 1
        return dict(jobs=job_count, deliveries=before,
                    result_rows=count, pending=queue.pending())
    finally:
        jobs.close(); queue.close(); store.close()


def exercise20():
    jobs, queue, store = Jobs(), LocalQueue(), manuals()
    try:
        job = jobs.submit(ALICE, 'changed-source', payload(), 0)
        jobs.relay(queue, 0)
        clock = Clock()
        try:
            work_once(jobs, queue, store, clock,
                      crash_at='checkpoint')
        except Crash:
            pass
        saved_stage = jobs.job(job['job_id'])['stage']
        store.set_acl('acme', 'manual-a', ['admin'])
        clock.advance(90)
        work_once(jobs, queue, store, clock, worker='worker-b')
        public = read_job(jobs, store, ALICE, job['job_id'],
                          clock.now)
        assert public['state'] == 'failed'
        assert public['result'] is None
        return dict(saved_stage=saved_stage,
                    state=public['state'], result=public['result'])
    finally:
        jobs.close(); queue.close(); store.close()


if __name__=='__main__':
    result=dict(exercise19=exercise19(),exercise20=exercise20())
    out=Path('results');out.mkdir(exist_ok=True)
    (out/'exercises.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))
