CHAPTER 3 - A MINIMAL ARCHITECTURE WE CAN TEST
Rodrigo Sillos | Tecnologia na Prática

Requirements: Python 3.10+, standard library only.
Editorial validation: Python 3.12.14. No external packages or credentials.
Extract the ZIP. Open a terminal in the laboratorio folder.

1. TESTS AND SOLUTIONS
python -m unittest discover -v
python experiments.py
python solutions.py

30 tests: 18 architecture/policy tests and 12 HTTP tests. HTTP tests open
ephemeral ports on 127.0.0.1 and shut down their servers afterward.
No external connections. If the environment blocks loopback, resolve the
local permission rather than exposing the server to a network.

2. SERVER (first terminal)
python http_api.py --port 8765 --mode good

If the port is occupied, use another, such as 8766, and pass --port 8766
to the client too. The server binds exclusively to 127.0.0.1.
Stop with Ctrl+C. No background service is installed.

3. CLIENT (second terminal in the same folder)
python client.py --topic returns
python client.py --topic refund --language en-US
python client.py --topic refund --token zen-demo
python client.py --topic sunday

Expected: Acme returns 30 days; Acme refunds 5 business days; Zen refunds
2 business days; sunday abstains. All policies are fictional. The first
command returns HTTP 200, answer, acme-returns-v2, synthetic cost 660.
request_id and elapsed_ms vary in actual local HTTP calls.

4. CONTROLLED FAILURES
Stop the server, restart with --mode timeout, and query returns.
Expected: HTTP 504, dependency_timeout, cost_microusd null.
This mode raises an exception immediately, without timing a provider.
Other modes: malformed, unsupported, unavailable, unexpected,
unknown_usage, expensive, incomplete, refused. Restore good afterward.
Clients cannot select modes in request bodies.

ARCHITECTURE
contracts.py: immutable values and normalized failure.
ports.py: repository, generator, and clock contracts.
policy.py: evidence selection and output validation.
service.py: use case without HTTP, files, or an SDK.
adapters.py: JSON/memory, stub, clocks, and demonstration identities.
bootstrap.py: composition root.
http_api.py / client.py: local server and client.
documents.json: 13 original documents with no evaluation oracle.
experiments.py: 12-scenario matrix and solutions.
solutions.py: exercises 5 and 6, including virtual-time doubles.

HTTP CONTRACT
POST /v1/answers
Content-Type: application/json
Authorization: Bearer acme-demo (or zen-demo)
Body: {"topic":"refund","language":"en-US"}
Extra fields are rejected. Topics: returns, refund, retention, p1, safety,
limit, hours, payroll, sunday, emergency. Not every identity has authorized
evidence for every topic. GET /health indicates the HTTP process only.
Identities are public teaching fixtures, NOT production authentication.
Request bodies are limited to 2048 bytes; the client sends Content-Length.

EXPERIMENTS
results/experiments.json contains 12 scenarios: 1 answer, 3 abstentions,
8 errors. Matrix time is virtual. Exercise 5 compares repositories.
Exercise 6 checks 1600+901=2501 ms (reject), 1600+900=2500 (accept),
and retrieval taking 2500 ms, which prevents generation from starting.
Costs are fictional: 2 micro-USD/input token and 6/output token. No pricing.

LIMITS
Teaching API, with no real model, TLS, authentication, global concurrency
limit, persistence, or production observability. http.server is not
recommended for production. Topics are preclassified. Returned text is
canonical text from a validated document, not free-form prose. JSON is
loaded at startup; restart after changing the corpus. Fixed 2026-10-14
snapshot. The service timeout is cooperative and checked after return;
it does not interrupt a blocked function. Budget rejection does not undo
consumption: expensive records 1560 even when rejected. Only model usage
is represented, not infrastructure cost.
