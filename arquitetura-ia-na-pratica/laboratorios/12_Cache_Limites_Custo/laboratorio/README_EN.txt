CHAPTER 12 - CACHING, LIMITS, AND COST PER TASK
Rodrigo Sillos | Tecnologia na Prática | R01 | October 15, 2026

REQUIREMENTS
Python 3.10+ with standard-library sqlite3. No API, network, or paid models.
Open a terminal in this laboratorio directory and run:

python -m unittest discover -v
python cache_scenarios.py
python cache_exercises.py

283 tests: 227 inherited and 56 new. 28 scenarios: 14 in each language.
An additional cohort compares ten requests per strategy (20 executions).
Outputs: results/scenarios.json and results/exercises.json.
New commands use the cache_ prefix; other commands belong to prior chapters.

NEW FILES
cache_cost.py: SQLite answer cache, transactional ledger, local gate.
cache_scenarios.py: PT/EN scenarios and with/without-cache cohort.
cache_exercises.py: executable worked exercises 23 and 24.
test_cache_cost.py: authorization, identity, invalidation, budget,
thread/connection concurrency, persistence, and reconciliation.

INTERPRETING VALUES
Fictional units, not currency. Each admitted task has fixed overhead 4;
compact/large calls cost 20/70. Cold complete = 24; warm = 4;
known timeout followed by a complete fallback = 94.
A miss reserves 4 + the policy's maximum generation units. An unknown
reservation does not expire automatically or disappear after restart.
Scenario results describe the final request; spent includes warm-ups.
With unknown cost, confirmed calls = 0 means no returned report, not evidence
that no call occurred.

LIMITATIONS
Gate: threads in one process, global capacity, no fair queue.
Single flight defers duplicates; it does not fan out the outer result.
Ledger: SQLite write transactions; tested with concurrent connections.
Cache: exact, per user, complete answers only, logical-time TTL.
64 entries, 16,384 bytes per payload; this does not bound database file size.
Administrative and settlement functions require trusted callers.
No invoice integration, distributed control, token bucket, remote calls,
load benchmark, encryption, or integration into Chapter 10's worker.
Initial authentication, pre-admission rejections, and infrastructure are
outside the cost convention. Values do not represent total ownership cost.

TESTS AND PERSISTENCE
Tests create their own scratch/ subdirectories and remove them on completion.
Cache and ledger accept SQLite paths for local persistence experiments.
Use the same logical-time reference when reopening a persistent cache.
The laboratory does not modify earlier chapter data.
