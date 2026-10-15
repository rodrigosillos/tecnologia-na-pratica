import json
from pathlib import Path
import sqlite3
import subprocess
import sys
from contextlib import contextmanager
import shutil
from uuid import uuid4
from async_jobs import Jobs, LocalQueue, Crash, IdempotencyConflict
from fixtures import ALICE
from job_worker import manuals, payload, work_once, read_job
from resilience import Clock


@contextmanager
def scratch_directory():
    base=(Path(__file__).resolve().parent/'scratch').resolve()
    base.mkdir(exist_ok=True)
    temp=(base/('run-'+uuid4().hex)).resolve()
    assert temp.is_relative_to(base) and temp.parent==base
    temp.mkdir()
    try:
        yield temp
    finally:
        assert temp.resolve().is_relative_to(base) and temp.parent==base
        shutil.rmtree(temp)


def restart_case(language='pt-BR',crash_at='checkpoint'):
    with scratch_directory() as temp:
        root=Path(temp);jpath=root/'jobs.db';qpath=root/'queue.db';spath=root/'sources.db'
        jobs=Jobs(jpath);queue=LocalQueue(qpath);store=manuals()
        try:
            target=sqlite3.connect(spath)
            try:store.db.backup(target)
            finally:target.close()
            job=jobs.submit(ALICE,'restart',payload(language),0)
            jobs.relay(queue,0)
            command=[sys.executable,str(Path(__file__).with_name('worker_cli.py')),
                     str(jpath),str(qpath),str(spath)]
            def execute(extra):
                return subprocess.run(command+extra,capture_output=True,text=True,
                    check=False,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
            first=execute(['--crash-at',crash_at])
            assert first.returncode==75,first.stderr
            after=jobs.job(job['job_id'])
            second=execute(['--now','100'])
            assert second.returncode==0,second.stderr
            public=read_job(jobs,store,ALICE,job['job_id'],110)
            final=jobs.job(job['job_id'])
            return dict(case='restart_'+crash_at,language=language,
                state=public['state'],attempts=final['attempts'],
                checkpoint_at_stop=after['stage'],
                result_rows=jobs.db.execute('SELECT count(*) FROM job_results').fetchone()[0],
                pending=queue.pending(),process_exits=[first.returncode,second.returncode],
                virtual_ms=json.loads(second.stdout)['virtual_ms'])
        finally:
            jobs.close();queue.close();store.close()


def run_case(case,language='pt-BR'):
    if case.startswith('restart_'):
        return restart_case(language,case.split('_',1)[1])
    jobs,queue,store=Jobs(),LocalQueue(),manuals();clock=Clock()
    extra={}
    try:
        job=jobs.submit(ALICE,'intent',payload(language),0,
                        validity_ms=20 if case=='expired' else 2000)
        jid=job['job_id']
        if case=='replay':
            extra['same_job']=jobs.submit(ALICE,'intent',payload(language),1)['job_id']==jid
        if case=='conflict':
            try:jobs.submit(ALICE,'intent',payload('en-US' if language=='pt-BR' else 'pt-BR'),1)
            except IdempotencyConflict:extra['conflict']=True
        if case=='duplicate':
            try:jobs.relay(queue,0,crash_after_publish=True)
            except Crash:pass
        jobs.relay(queue,0)
        if case=='cancelled':jobs.cancel(ALICE,jid)
        if case=='expired':clock.advance(20)
        if case=='retry':
            work_once(jobs,queue,store,clock,transient=True);clock.advance(200)
        if case=='dead_letter':
            for _ in range(3):
                work_once(jobs,queue,store,clock,transient=True);clock.advance(200)
        work_once(jobs,queue,store,clock)
        if case=='duplicate':work_once(jobs,queue,store,clock)
        if case=='revoked_read':store.set_acl('acme','manual-a',['admin'])
        public=read_job(jobs,store,ALICE,jid,clock.now);row=jobs.job(jid)
        return dict(case=case,language=language,state=row['state'],attempts=row['attempts'],
            completed_steps=row['stage'],has_result=public['result'] is not None,
            result_rows=jobs.db.execute('SELECT count(*) FROM job_results').fetchone()[0],
            pending=queue.pending(),virtual_ms=clock.now,**extra)
    finally:jobs.close();queue.close();store.close()


def run_scenarios():
    names=['complete','replay','conflict','duplicate','restart_checkpoint',
           'restart_result','retry','dead_letter','cancelled','expired','revoked_read']
    runs=[run_case(name,language) for language in ('pt-BR','en-US') for name in names]
    return dict(cases=len(runs),language_pairs=len(names),runs=runs,
        measurement='SQLite commits and controlled process restarts; synthetic virtual time, no external services')


if __name__=='__main__':
    result=run_scenarios();out=Path('results');out.mkdir(exist_ok=True)
    (out/'scenarios.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))
