"""One local delivery in a fresh interpreter; exit 75 simulates a stopped worker."""
import argparse
import json
from async_jobs import Jobs, LocalQueue, Crash
from pipeline import Pipeline
from resilience import Clock
from job_worker import work_once


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('jobs');parser.add_argument('queue');parser.add_argument('sources')
    parser.add_argument('--now',type=int,default=0)
    parser.add_argument('--crash-at',choices=['checkpoint','result'])
    args=parser.parse_args()
    jobs=Jobs(args.jobs);queue=LocalQueue(args.queue);store=Pipeline(args.sources)
    clock=Clock(args.now)
    try:
        state=work_once(jobs,queue,store,clock,crash_at=args.crash_at)
        print(json.dumps(dict(state=state,virtual_ms=clock.now)))
        return 0
    except Crash:
        print(json.dumps(dict(state='stopped',virtual_ms=clock.now)))
        return 75
    finally:
        jobs.close();queue.close();store.close()


if __name__=='__main__':raise SystemExit(main())
