CHAPTER 16 - SECURITY BEYOND THE PROMPT
Rodrigo Sillos | Tecnologia na Prática | R01 | October 15, 2026

REQUIREMENTS
Python 3.11 or newer; standard library. No API, key, or network.
Open a terminal in this laboratorio directory. Use python or py for your installation.

RUN
python -m unittest discover -s .
python -m unittest test_security -v
python security_scenarios.py
python -c "from security_exercises import exercise31,exercise32; print(exercise31()); print(exercise32())"

VERIFIED RESULTS
532 passing tests: 460 inherited and 72 new.
20 scenarios in two languages = 40 runs, reproduced in results/scenarios.json.
Per language: 3 answered, 15 blocked, 1 abstained, 1 pending.
Matrix: zero destination tasks, one pending intent per language.
A separate integration test legitimately approves and creates one synthetic task.
Exercises 31/32: results/exercises.json. Scripts print JSON and do not overwrite saved results.

NEW FILES
security_gate.py: host identity/capability, minimal context, strict schema,
revalidation, exact fact, HTML encoding, and pending proposal through Chapter 15.
security_scenarios.py: scripted adversarial candidates, benign controls, residual risk.
security_exercises.py: executable solutions for Exercises 31 and 32.
test_security.py: isolation, fields, revocation, presentation, and approval tests.

CONTRACTS
Source: up to 4096 Python characters; candidate: up to 768 UTF-8 bytes.
Positions: Python Unicode indexes, inclusive start/exclusive stop, not byte offsets.
One candidate per instance, including an invalid candidate. Not a global abuse limit.
The model may select a fact, abstain, or propose when the host permits it.
It cannot choose identity, tenant, destination, project, approval, or execution.
context() labels the source, but that label is not a security boundary.
The Python process and local administration are trusted in the threat model.

LIMITATIONS
No inference: adversarial output is injected directly at the validation boundary.
This does not measure attack success against an LLM or production performance.
A false source can pass: poisoned_fact answers 99 days. Citation does not prove truth.
The regex does not understand negation, examples, jurisdiction, or effective dates in general text.
render_quote protects HTML text context, not SQL, shell, JavaScript, or URLs.
No real authentication, process/network isolation, immutable audit, or global quotas.
Serial revalidation does not resolve distributed check/use races.
Boundary events are local/in-memory and not joined to inherited telemetry.
No real private source is used. sink.invalid is text only and is never contacted.

CONTINUITY
Previous modules/tests remain unchanged; integrations are explicit.
Prior guides remain in the corresponding chapter directories.
Tests may create scratch and __pycache__ with local execution files only.
Editorial teaching proof, not a production security service.
