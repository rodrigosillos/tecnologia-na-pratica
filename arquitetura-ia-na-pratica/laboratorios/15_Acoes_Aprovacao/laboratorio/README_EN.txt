CHAPTER 15 - EXTERNAL ACTIONS AND HUMAN APPROVAL
Rodrigo Sillos | Tecnologia na Prática | R01 | October 15, 2026

REQUIREMENTS
Python 3.11+ and the standard library with sqlite3. No SDK or credentials.
Open a terminal in this laboratory directory and run:

python -m unittest discover -v
python action_scenarios.py
python action_exercises.py

460 tests: 400 inherited and 60 new. 36 scenarios: 18 per language.
action_scenarios.py writes results/scenarios.json; action_exercises.py prints
the solved exercises. results/exercises.json is included in the delivery.
Commands from earlier chapters remain and may overwrite results/scenarios.json
with their own scenarios. Run action_scenarios.py again to reproduce Chapter 15.

FILES
actions.py: parser, intent, preview, decision, persistence, executor,
reconciliation, and a simulated destination in a separate SQLite database.
action_scenarios.py: fixtures, faults, and 18 PT/EN situations.
action_exercises.py: complete Exercises 29 and 30.
test_actions.py: 60 new tests; earlier modules and tests preserved.

DESIGN
Alice requests; Carol reviews. Both belong to fictional tenant acme.
Proposals accept only tool=prepare_task, project=ops, and an allowed topic.
Chapter 14's workflow compares manuals. Returns: 45 -> 30 days.
Shipping: 3 -> 3, no discrepancy; that topic produces no task.
Preview and submission use the same structured payload and versioned operation.
Approval binds intent ID and hash, reviewer and time; default TTL 30 virtual s.
Grant is trusted fixture administration; Actor is not real authentication.
The reviewer may see the ops fact projection, not unrestricted document bodies.
Sources and permissions are revalidated before acting.

STATES AND RECOVERY
pending -> approved/rejected; approved -> dispatching after checks.
Confirmed response -> succeeded; timeout/ambiguous adapter error -> unknown.
Cancel only before dispatch. Expiry/revocation block new submissions.
Receipt lookup can acknowledge an earlier effect after revocation.
Retry uses the same key, identical parameters, and at most two claimed attempts.
The destination retains keys permanently in this simulation, scoped by tenant.
Two separately approved intents may create matching tasks:
technical deduplication is not business deduplication.
Use recover only after establishing that the previous executor has stopped.

RESULTS
Normal: 1 attempt, 1 call, 1 effect.
Timeout after commit: unknown, 1 effect; lookup completes without resubmission.
Timeout before: unknown, 0 effects; valid retry: 2 calls, 1 effect.
Crash before call: 2 claimed attempts, 1 call, 1 effect.
Restart after commit: 1 call and 1 effect, receipt reconciled.
Ex29: matching hashes, second intent pending, wrong hash rejected, 1 effect.
Ex30: unknown -> succeeded after expiry/revocation; 1 creation and 1 lookup.

LIMITATIONS
Fictional data. Virtual time, not a benchmark. No network or real external effects.
Serial execution, no leases, distributed fencing, broker, or continuous worker.
Restart closes/reopens connections while retaining the in-memory document fixture.
No atomicity between source revalidation and destination commit.
A hash is not a signature; storage, administration, and Python code are trusted.
Transactional audit is not immutable; rejected decisions are not audited.
Stored captures would require protection and retention policy in production.
Cumulative cost/queue/telemetry modules are not automatically integrated.
Temporary databases are created under scratch and removed on completion.
No advertisement, publication, email, or external service is changed.
