CHAPTER 17 - DEPLOYMENT, MIGRATIONS, AND OPERATIONAL RECOVERY
Rodrigo Sillos | Tecnologia na Prática | R01 | October 15, 2026

RUN (Python 3.11+, standard library, no credentials or network)
Open a terminal in this laboratorio directory:
python -m unittest discover -s .
python -m unittest test_releases -v
python release_scenarios.py
python -c "from release_exercises import exercise33,exercise34; print(exercise33()); print(exercise34())"

DELIVERY
602 tests: 532 inherited and 70 new. 20 PT/EN scenarios = 40 runs.
results/scenarios.json: reproducible states; results/exercises.json: solutions 33/34.
Commands print outcomes without replacing the reference JSON files.

NEW FILES
releases.py: manifest, evaluation, migration, promotion/rollback, pinned jobs,
SQLite API backup, and restoration requiring explicit resumption.
release_scenarios.py: fixtures, virtual clock, temporary files, and matrix.
release_exercises.py: executable solutions for Exercises 33/34.
test_releases.py: failure, integrity, two connections, recovery, and compatibility checks.

CONTRACTS
r1/v1: status and text; schema 1 or 2.
r2/v2: adds response provenance and an optional column; requires schema 2.
broken: synthetic regression returns 999; passes 4/6 checks and cannot be promoted.
Evaluation: three cases per language, six total; valid for 15 virtual time units.
Promotion: current manifest/code/index, 6/6 evaluation, compatible schema, expected epoch.
Rollback: previously active release, same checks; epoch advances, schema 2 remains.
Jobs: release pinned at admission; saved results revalidate current sources.
Backup: local registry plus logical digest JSON; excludes sources and external destinations.
Restore: new destination, never overwrites; begins in recovery. Evaluate and resume before serving.

LIMITS AND INTERPRETATION
No LLM: prompts are inventory; responses and faults are deterministic.
index_digest covers local chunk projections, not a remote vector index.
CORE lists modules covered by the digest; this is not a complete dependency signature.
Real SQLite migration, but no large backfill or destructive contraction phase.
No cluster, live canary, distributed worker, external fencing, real identity, or secret vault.
Operator, code, and storage are trusted. Hashing does not authenticate artifact publishers.
Registry and sources are separate databases; no distributed atomicity spans them.
Before/after-commit exceptions and reopening a connection are not physical-failure tests.
Restoration restores the backup's epoch too; production would need old-worker isolation.
The restore case loses one later admission. It does not measure temporal production RPO/RTO.
Rollback does not reverse external effects. Restoration does not automatically recover current permissions.
The in-memory source stays alive during the exercise; only the registry is restored.
Inherited modules remain unchanged, but their integration is not automatic.

Temporary files: scratch, __pycache__. No real service is changed.
Earlier guides remain in their corresponding chapter directories.
