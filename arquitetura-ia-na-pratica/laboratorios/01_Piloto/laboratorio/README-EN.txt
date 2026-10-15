LAB 01 - KNOWLEDGE COPILOT
Rodrigo Sillos | Tecnologia na Prática | Pilot R01, October 14, 2026

REQUIREMENTS
Python 3.10 or later. Standard library only. No package installation,
keys, network access, or APIs. All data is synthetic.
Open a terminal in this folder. On Windows, python may be py -3;
on other systems it may be python3. Use the command available to you.

RUN
python --version
python -m unittest -v
python copilot.py --policy naive --out results/naive.json
python copilot.py --policy guarded --out results/guarded.json
python copilot.py --policy candidate --out results/candidate.json
python copilot.py --policy abstain --out results/abstain.json
python solutions.py

Tests should finish with OK (16 tests). solutions.py executes both worked
exercises and the relaxed-limit experiment. You may also run it directly:
python copilot.py --policy candidate --latency-ms 5000 --budget-microusd 2000

EXPECTED RESULTS
Policy     Accepted/eligible  Correct abstentions  Disclosures  Suite
naive      5/8                2/4                  2            fail
guarded    8/8                4/4                  0            pass
candidate  3/8                3/4                  1            fail
abstain    0/8                4/4                  0            fail
With limits of 5,000 ms and 2,000 microdollars, candidate accepts 5/8
but still fails the suite. Its total synthetic cost is 6,800 microdollars.

INVESTIGATION
Inspect individual cases in the results JSON files. Distinguish
correct_answer, on_time, within_budget, and accepted_task. The main
fraction uses eight eligible questions, not all twelve requests.
No result is a provider benchmark. The candidate replay is an authored,
controlled sequence, not an AI execution. The lookup duration of 20 ms is
also a synthetic input. Zero cost means zero API cost in the scenario,
not zero total operating cost. 1,000,000 microdollars = US$1.

CONTRACT AND LIMITATIONS
Snapshot: 2026-10-14. Validity uses [start, end).
Topics are preclassified. Identity and role are trusted test inputs.
There is no generated prose. fact_id represents a closed fact;
expected_fact belongs only to the evaluator. Companies and manuals are
fictional. There are 13 documents and 12 development cases, no holdout.
Disclosure detection covers this contract's citations, not free text.
No HTTP, actions, queue, database, or real spending enforcement is
implemented. Passing the local suite does not certify production use.

FILES
copilot.py - implementation and command-line entry point
fixtures.json - bilingual data, oracle, and synthetic events
test_copilot.py - 16 behavioral and boundary tests
solutions.py - executable exercises and experiment
results/ - reference execution; commands may overwrite reports

If your results differ, check your Python version and keep the failure
message. Do not alter the oracle to make code pass. Use a copy for new
experiments; keep corpus, case, and expectation coherent and versioned.
