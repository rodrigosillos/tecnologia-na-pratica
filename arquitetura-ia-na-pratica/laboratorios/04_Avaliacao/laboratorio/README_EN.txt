CHAPTER 4 LAB - EVALUATION BEFORE OPTIMIZATION
Python 3.10+; tested with Python 3.12.14. Standard library only.
Extract the package and open a terminal in this folder. No installation,
server, network connection, provider account, or credentials are required.

1. Run: python -m unittest discover -v
   Expected: 26 tests, OK.
2. Run: python evaluation.py
   baseline: 24/24; fast_unsafe: 14/24; refuse_all: 4/24;
   missing_meter: 24/24, blocked because usage is unknown.
3. Run: python solutions.py
   Exercises 7 and 8 with executable assertions and full results.
4. Inspect results/evaluation.json for rows, slices, gates, paired
   comparison, and hashes. All durations and costs are synthetic.

cases.v1.json: 24 authored cases, 12 groups, two language versions.
All cases are visible regression data; there is no blind holdout here.
policy.v1.json: teaching thresholds fixed before comparison.
systems.py: system variants receive Request only, without gold labels.
app/: preserved chapter-3 modules and 13 synthetic documents.
evaluation.py: evaluator outside the system, metrics, and manifest.
solutions.py: solved exercises 7 and 8.

HUMAN REVIEW
The command creates results/human_review_en.csv and revisao_humana_pt.csv,
12 pairs per language, with no verdicts filled in. Use the chapter rubric,
cases.v1.json, and app/documents.json as factual references. Fill verdict
(A, B, tie, or insufficient), evidence (source excerpt and explanation),
severity (critical, major, or minor), and reviewer (local identifier).
Review independently before discussing disagreements. The A/B key is kept
separately in results/chave_revisao.json; open it after rating the pairs.
Costs and durations are excluded. This is a review worksheet, not evidence
of a completed blind human study. No human or LLM rated these pairs as part
of this delivery. human_review is a routing decision only: it creates no
queue, task, or contact with a person.

RE-RUNNING
evaluation.py overwrites reports in the output folder. Preserve completed
worksheets by copying them or selecting a different output directory:
python evaluation.py --out results/another_run
The manifest records dataset, policy, and code bytes. A hash does not prove
label correctness. Changing criteria after seeing results requires a new
revision and a fresh comparison against the baseline.

INTERPRETATION
The 24 rows form 12 related fact groups; translations are not independent
observations. Bootstrap resamples groups 2,000 times with seed 7.
The fast_unsafe minus baseline difference is -41.67 percentage points;
the descriptive percentile interval is -66.67 to -16.67 points. This is a
synthetic demonstration, not a real-traffic quality estimate.
There is no LLM judge, model benchmark, or billing. Exact match deliberately
tests closed facts rendered as canonical text, not open-ended paraphrases.
