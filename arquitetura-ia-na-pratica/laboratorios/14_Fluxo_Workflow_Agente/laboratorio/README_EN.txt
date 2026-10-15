CHAPTER 14 - DETERMINISTIC FLOW, WORKFLOW, OR AGENT?
Rodrigo Sillos | Tecnologia na Prática | R01 | October 15, 2026

REQUIREMENTS AND EXECUTION
Python 3.11+ with the standard library and sqlite3. No APIs, network, or paid models.
Open a terminal in this laboratory directory:

python -m unittest discover -v
python control_scenarios.py
python control_exercises.py

400 tests: 339 inherited and 61 new. 32 cases: 16 per language.
Additional comparison: 10 tasks per mode (20 executions).
Commands overwrite results/scenarios.json and results/exercises.json.
control_ commands belong to this chapter; earlier commands remain.

NEW FILES
control.py: strict parser, session, tools, meter, workflow,
simulated planner, and bounded controller.
control_scenarios.py: adverse proposals, source checks, and comparison.
control_exercises.py: solved Exercises 27 and 28.
test_control.py: 61 contract and outcome tests.

COMPARISON RESULTS
Workflow: 10/10 complete, 42 tools, 0 planning calls,
42 u, 4.2 u per completion, and virtual p95 of 20 ms.
Simulated planner: 10/10 complete, 42 tools, 42 planning calls,
126 u, 12.6 u per completion, and virtual p95 of 55 ms.
Eight normal tasks and two with one transient read per mode.
Both approaches allow one bounded read retry.
No LLM was executed: proposals are controlled rules/scripts.

CONTRACTS
JSON up to 512 bytes, unique keys, exact fields, and short strings.
Tools: read, compare, finish, stop. No code, URLs, or external writes.
Tenant, user, documents, language, and limits are host-controlled.
Captures and results stay in the host; completion requires evidence and revalidation.
One execution per Session. Do not reuse a Session for a new request.
Defaults: 8 proposals, 30 units, 150 virtual ms, up to 2 identical proposals.
Tariffs: planning 2 u/7 ms; read 1/5; compare 1/3; finish 1/2;
stop 0/0. Admitted tools that fail are also accounted for.
These are chapter-specific units; do not mix with earlier tariffs.

LIMITATIONS
Agent loop with a simulated planner, no learning or real model.
Logical proposal boundary, not a sandbox for hostile Python code.
Local sequential execution, no integrated persistence/replay, worker, or ledger.
Cumulative files do not imply automatic integration.
Virtual deadlines do not interrupt blocked functions. Cancellation is cooperative.
The detector counts repeated canonical proposals, not every type of cycle.
Version and permission are checked at a read boundary, not forever.
Unexpected storage exceptions can propagate. No external effects, real billing,
exactly-once guarantee, or evaluation of a deployed LLM.
Failure hooks are trusted experiment code, not planner tools.
