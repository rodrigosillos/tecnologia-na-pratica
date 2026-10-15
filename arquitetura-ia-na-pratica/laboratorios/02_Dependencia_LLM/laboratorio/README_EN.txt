CHAPTER 2 - THE MODEL BOUNDARY
Rodrigo Sillos | Tecnologia na Prática

Requirements: Python 3.10 or later; standard library only.
No package installation, network, key, model, or billing is involved.
Open a terminal in this folder (laboratorio) and run:

python -m unittest discover -v
python boundary.py --out results/boundary.json
python solutions.py

36 tests: 16 from chapter 1 and 20 new tests. Editorial run: Python 3.12.14.
Expected report: 12 scenarios, 11 simulated attempts, 2 accepted answers,
1 business abstention, and 9 failures. Known cost: 6150 micro-USD;
one unmetered attempt; total cost and cost per accepted answer: null.
These numbers are NOT model measurements or provider prices.
Durations, tokens, and costs come from authored teaching fixtures.

FILES
boundary.py: toy tokenization, context budget, cosine, strict JSON parser,
response validation, and reporting.
scenarios.json: 12 authored envelope/output scenarios with text chunks.
fixtures.json / chapter1.py: synthetic chapter 1 data and rules.
test_boundary.py: 20 boundary and demonstration tests.
test_chapter1.py: 16 regression tests.
solutions.py: executable solutions to exercises 3 and 4.

EXPERIMENT WITHOUT LOSING THE ORIGINAL
Copy scenarios.json before editing. Change s02 to completed while leaving
its truncated text unchanged: its class becomes invalid_json. Restore the
file and compare reports. Do not put real records in these fixtures.

LIMITS
No model, trained embedding, network stream, SDK, or HTTP service is used.
Topics are preclassified; evidence uses fact identifiers. expected_fact
is an evaluation oracle only, read after the decision. Free-text entailment,
transport, authentication, and remote cancellation are outside this lab.
The 8192-byte limit checks an already assembled string; production must
also bound incoming buffers before allocation. This is not a finished SDK.
Document validity uses the 2026-10-14 snapshot, not the current clock.
Context planning uses synthetic counts, never toy_tokens as a provider
estimator. The local shape validator is not a general JSON Schema engine.
