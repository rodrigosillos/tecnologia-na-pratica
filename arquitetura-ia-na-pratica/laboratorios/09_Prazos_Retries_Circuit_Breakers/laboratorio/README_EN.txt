CHAPTER 9 — DEADLINES, RETRIES, AND CIRCUIT BREAKERS
R01 | Python 3.10+ with sqlite3 | Standard library only

Open a terminal in this laboratorio directory and run:
  python -m unittest discover -v
  python experiments.py
  python exercises.py

131 tests: 89 unchanged inherited tests and 42 new tests.
experiments.py writes results/scenarios.json: ten control experiments,
eight integrations (four per language), the solved exercises, and a retry
amplification tree. exercises.py writes results/exercises.json (17 and 18).
These result files are regenerated; no user data is needed.

NEW FILES
resilience.py: virtual clock, policy, scripted provider, finite retry quota,
circuit breaker, and attempt controller.
integration.py: connects the controller to the unchanged Chapter 8 contract.
experiments.py: reproducible cases; exercises.py: worked solutions.
test_resilience.py: boundaries, faults, cancellation, and integration tests.

CONTINUITY
Earlier modules remain for comparison and regression coverage. scenarios.py
and solutions.py belong to Chapter 8; previous_solutions.py belongs to 7.
Run experiments.py and exercises.py for this chapter's results.
service.py and client.py retain Chapter 8 events and rules.
Do not rename modules or remove base/ or schemas/.

EXPERIMENT POLICY
1200 ms total deadline; up to 300 ms per attempt; 100 ms terminal reserve;
50 ms minimum useful attempt. Three attempts maximum INCLUDING the first.
Discrete full jitter: 0..min(400,100*2^(r-1)) ms. Seed 7 is for repeatability.
Retry-After is already normalized to milliseconds and is never shortened.
Default retry quota: two extra attempts, no refill. Circuit: three eligible
availability failures, 500 ms cooldown, one half-open probe. Exercise 18 uses
a threshold of two. Scenario-specific time budgets and quotas are explicit.
A Controller represents one operation; its deadline never resets.
Multiple operations can share a CircuitBreaker and a RetryBudget.

LIMITS
Milliseconds are virtual. No real waits, HTTP, LLMs, credentials, charges,
or performance benchmark. The provider simulates duration and status only;
grounded answers remain extractive over the earlier fictional data.
Integration shares a deadline across questions but does not model actual
retrieval CPU, serialization, or transport time. The reserve is illustrative.
The circuit counts consecutive eligible failures, not a rolling window.
429, contract errors, and cancellation are neutral for health in this policy.
A neutral half-open probe conservatively reopens the circuit. Old permits
cannot heal a newer circuit generation. Single-threaded synchronous model;
real concurrency requires synchronization, and processes are not coordinated.
Cancellation is observed at checkpoints, not proof of remote interruption.
read_only=False prevents retrying an uncertain side effect; it implements
neither writes nor idempotency. Retry quota does not limit initial attempts.

results/ contains the reference execution. The chapter explains calculations,
design choices, and the remaining work for production. Laboratory timeout
values are not universal operational recommendations.
