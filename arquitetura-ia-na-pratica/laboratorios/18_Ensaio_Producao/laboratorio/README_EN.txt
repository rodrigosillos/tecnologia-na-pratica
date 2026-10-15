CHAPTER 18 - PRODUCTION READINESS EXERCISE AND ARCHITECTURE REVIEW
Python 3.11+; standard library; offline; no credentials.

From laboratorio:
  python -m unittest discover -s .
  python -m unittest test_readiness -v
  python readiness_scenarios.py
  python -c "from readiness_exercises import exercise35,exercise36; print(exercise35()); print(exercise36())"

669 cumulative tests: 602 inherited, 67 new. Matrix: 18 cases x 2 languages.
Solved exercises 35 and 36. results/scenarios.json, exercises.json, and review.json
contain reproduced delivery results. These commands do not overwrite them.
Earlier scenarios remain available in their chapter-specific modules.

Integration: bounded admission + jobs/outbox/queue + dependency controller +
security boundary + capture/comparison + read-time source revalidation.
New files: readiness.py, readiness_scenarios.py, readiness_exercises.py,
test_readiness.py. Earlier modules are unchanged.

Provider status and duration are simulated; output candidates are scripted.
No real LLM, network, price, tokens, or external action. Time and faults are synthetic.
The global cap counts unfinished jobs, not broker messages. Every producer on
this path must use BoundedJobs. No tenant fairness. Pausing admission does not
cancel accepted work.

SQLite commits are real; time and the event trace remain in memory. The restart
scenario reopens connections: it does not restart the process or restore a backup,
and it retains the source fixture, circuit, clock, and trace. It is no disaster test.
Temporary databases are placed under scratch and removed after each case.

poisoned_fact passes by exposing a limitation: a false source in an allowed
format produces a faithful but policy-incorrect answer. release_decision organizes
declared references, does not establish their truth, and authorizes no deployment.
The delivered review retains hold because live quality and operations are unmeasured.
The suite provides local evidence, not certification.

Caching, routing, actions, and the release registry remain separate from this
worker, although their tests are preserved in the cumulative suite.
