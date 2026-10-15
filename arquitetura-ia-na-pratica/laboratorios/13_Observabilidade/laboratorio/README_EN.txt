CHAPTER 13 - OBSERVABILITY THAT SUPPORTS DECISIONS
Rodrigo Sillos | Tecnologia na Prática | R01 | October 15, 2026

REQUIREMENTS AND EXECUTION
Python 3.11+ with the standard library and sqlite3. No APIs, network,
or paid model calls. Open a terminal in this laboratory directory:

python -m unittest discover -v
python observe_scenarios.py
python observe_exercises.py

339 tests: 283 inherited and 56 new. 24 cases: 12 per language.
Additional regression: 3 variants x 20 requests = 60 executions.
Commands overwrite reproducible outputs under results:
scenarios.json, exercises.json, and example_trace.json.
observe_ commands belong to this chapter; earlier commands remain.

NEW FILES
observability.py: original trace format, allowed attributes, measurements,
percentiles, histograms, and observation of Chapter 12 contracts.
observe_scenarios.py: PT/EN cases and a controlled causal comparison.
observe_exercises.py: Exercises 25 and 26; no alert dispatch.
test_observability.py: 56 tests for signals, privacy, and outcomes.

COMPARISON RESULTS
Baseline: p95 102 ms, 480 u, 20 calls, 20/20 good.
Regression: p95 278 ms, 830 u, 25 calls, 0/20 good.
Queue only: p95 182 ms, 480 u, 20 calls, 0/20 good.
Every group has 20 complete answers and 5 exported traces.
Measurements use all requests independently of trace sampling.
Good = eligible, complete, quality passed, and duration <= 150 ms.
The 99% objective and exercise thresholds are teaching choices.

UNITS AND TIME
Fictional units: 4 per admitted task, compact 20, large 70.
Prescribed virtual time: source 3 ms (12 for slow reads), lookup 2,
write/admission/reservation/settlement 1, finalization 20, and scripted
model time. Slow queue adds 80 ms. This is not a real benchmark.
Warm case: preparation is outside its final 23 ms / 4 u observation.
Unknown cost: 1 attempt started, 0 u settled, and 94 u held.
Observed holds are new commitments; their sum does not replace the
ledger's current balance after subsequent reconciliations.

LIMITATIONS
Original trace format, not an OpenTelemetry SDK or protocol.
Sequential execution, no distributed worker or streaming/first-token time.
Deterministic IDs are internal fixtures, not an anonymization scheme.
The in-memory collector stores records for a finite experiment, not a
production metrics backend. Maximum 64 spans per trace; sampling lowers
export volume, not local span construction. Merged histograms must come
from local functions with identical boundaries. Quality is deterministic
over closed facts; unknown is not good in the conservative SLI.
Unexpected executor exceptions may prevent final recording/export.
Exporter failure is contained but does not ensure an out-of-process alert.
page_decision returns text, validates no temporal selection, sends nothing.
No evidence of production capacity, availability, commercial cost, or
open-ended quality. Production collection and retention need further design.
