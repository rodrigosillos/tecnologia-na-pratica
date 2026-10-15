CHAPTER 10 - ASYNCHRONOUS JOBS, QUEUES, AND IDEMPOTENCY
R01 | Python 3.10+ with sqlite3 | Standard library only

From the laboratorio directory, run:
  python -m unittest discover -v
  python job_scenarios.py
  python job_exercises.py

176 tests: 131 unchanged inherited tests and 45 new tests. There are 22
scenarios (11 per language). Results are written to results/scenarios.json
and results/exercises.json. This chapter's exercises are 19 and 20.

NEW FILES
async_jobs.py + jobs.sql: submission, idempotency keys, outbox, leases,
fencing, checkpoints, result persistence, cancellation, and local quarantine.
job_worker.py: extractive comparison of two fictional manuals.
worker_cli.py: one delivery executed in a fresh Python process.
job_scenarios.py: scenarios and controlled restarts.
job_exercises.py: worked solutions. test_jobs.py: 45 new tests.

EXECUTION AND TEMPORARY FILES
Most scenarios use in-memory databases. Restart cases create jobs, queue,
and source SQLite databases inside a unique scratch/ subdirectory.
One worker process exits with code 75 after a checkpoint or result commit;
another process reopens the databases and continues. Exit 75 is intentional.
Connections are closed, then only that temporary subdirectory is removed.
No personal files are read. The laboratory directory must be writable.
Two tests use independent connections and threads to contend for submission
and claiming. They are not load tests or multi-server trials.

MODEL CONTRACT
Operation compare-manuals-v1; payload: language + two ordered documents.
Keys are scoped by tenant, principal, operation, and intent key.
Same payload/key returns the existing job; different payload conflicts.
Jobs and outbox commit in one database; the queue is another SQLite database.
The relay can publish twice; workers inspect persisted job state.
Three claims maximum; 100 ms lease and visibility; 2000 ms job validity.
A transient failure schedules a new claim after 200 ms. Time is virtual.
Each capture consumes 10 simulated ms. Queueing does not reset job validity.
Checkpoint and progress commit together; result and success commit together.
ACK follows result commit or an observed terminal job state.

LIMITS
No HTTP, remote broker, network, LLM, credentials, or paid calls.
202/200 and Location describe a local adapter, not an HTTP server.
Comparison recognizes two fixed sentence patterns (returns and shipping) in
each language. It is neither arbitrary document understanding nor a benchmark.
Controlled process exit is not a power-loss or disk-failure test.
One stored result is a local database property, not exactly-once execution.
Cancellation prevents new worker writes; it does not prove remote work stopped.
A completed result can become unavailable after revocation or source changes.
Authorization is checked against a consistent source snapshot on reading.
Incremental IDs are not secrets; identity comes from a trusted caller.
No deduplication TTL, result cleanup, automatic redrive, automatic visibility
renewal, periodic scheduler, or cross-tenant fairness is implemented.
dead_letters is a quarantine table, not a managed broker's DLQ.

CONTINUITY
Earlier modules remain unchanged for regression tests. experiments.py and
exercises.py are Chapter 9; scenarios.py and solutions.py are Chapter 8.
Use job_scenarios.py and job_exercises.py for this chapter.
