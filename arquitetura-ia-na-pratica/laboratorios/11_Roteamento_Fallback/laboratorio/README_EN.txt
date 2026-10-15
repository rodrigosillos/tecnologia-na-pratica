CHAPTER 11 - ROUTING AND FALLBACK WITH EXPLICIT CRITERIA
R01 | October 15, 2026 | Rodrigo Sillos | Tecnologia na Prática

REQUIREMENTS AND COMMANDS
Python 3.10+ with sqlite3. Standard library only; no pip, network, secrets,
or model calls. Run from this directory:

python -m unittest discover -v
python routing_scenarios.py
python routing_exercises.py

227 passing tests: 176 inherited from Chapter 10 and 51 new.
Reports are written to results/scenarios.json and results/exercises.json.
Earlier modules remain available: experiments.py and exercises.py belong to
Chapter 9; job_scenarios.py and job_exercises.py belong to Chapter 10.
Running those earlier programs replaces reports with the same filenames;
the delivered reports already contain Chapter 11 results.

IMPLEMENTATION
routing.py: fictional registry, revision/task/language approval, eligibility,
shared budgets, call limits, comparison validation, partial results, and
source revalidation. routing_scenarios.py runs 14 scenarios per language,
28 runs, plus a ten-request cohort for two strategies, another 20 runs.
routing_exercises.py contains solved Exercises 21 and 22.
test_routing.py contains the 51 new checks.

DATA AND EXPECTED RESULTS
Chapter 10 manuals: returns 45/30 days; shipping 3/3 days. Delta is B minus A.
Extraction uses fixed patterns, not an LLM.
compact: 20 units, timeout 60 ms; large: 70 units, timeout 140 ms;
remote: 10 units, timeout 40 ms, external zone denied by default.
Names do not denote commercial products. Scripted durations are respectively
40, 90, and 20 virtual ms. Finalization takes another 20 virtual ms.
Each call consumes its entire reservation, even on failure. These fictional
admission units are not dollars or any other currency.

Normal: full, compact, 1 call, 20 units, 60 ms.
Transient fallback: full, compact + large, 2 calls, 90 units, 150 ms.
Partial with a 20-unit cap: partial, returns only, missing=['shipping'].
Refusal: abstain, without trying another model.
Authored cohort: cascade 12 calls / 340 units / 780 summed virtual ms;
large_only 10 calls / 700 units / 1100 summed virtual ms. Both produce ten
full outputs. These are not measurements of real LLM performance or quality.

EXERCISES
21: cap 89, compact fails. Remaining 69 cannot admit large's 70-unit charge;
remote is forbidden. Result: abstain, ['compact'], 20 units.
22: cap 20, compact returns a validated returns comparison only.
Result: partial, missing=['shipping'], delta=-15, 20 units.

LIMITS
Approval records are authored fixtures, not empirical quality evaluations.
Context limits count UTF-8 bytes in captured envelopes, not tokens.
Virtual timeout does not prove remote cancellation or billing behavior.
No HTTP, streaming, traffic redirection, cache, trained router, shared concurrent
ledger, automatic health updates, or load measurements are implemented.
The router reuses Chapter 10 capture/authorization but is not installed in its
durable worker; doing that would require persisting attempt reservations.
Inherited restart tests create and remove their own scratch subdirectory after
closing databases. Editorial files are not changed.
Real adapters require evidence for destination, retention, contract, token
limits, output limits, prices, unknown costs, and task/version/language quality.
