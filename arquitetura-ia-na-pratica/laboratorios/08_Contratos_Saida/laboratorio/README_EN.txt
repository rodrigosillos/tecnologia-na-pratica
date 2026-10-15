R04 ENGLISH EDITION
English entry points select en-US explicitly. Original bilingual fixtures
and Portuguese entry points remain unchanged. See ENGLISH_EDITION_R04.txt.

CHAPTER 8 - OUTPUT CONTRACTS AND USABLE APIs
Python 3.10+ with sqlite3. Standard library only; no network or paid services.

Inside laboratorio:
python -m unittest discover -v
python scenarios.py
python solutions_en.py

89 tests (42 inherited + 47 new). 14 scenarios (7 per language).
Scenarios and exercises write JSON into the local results directory.
Fictional data in in-memory SQLite. Earlier chapter databases are not changed.
See scenarios.request and solutions.exercise15/exercise16.

FILES
contract.py: explicit validation, JSON encoding, event framing.
service.py: in-memory adapter; trusted caller supplies authenticated actor identity.
client.py: byte reader, correlation, state machine, truncation detection.
schemas/: structural JSON Schema 2020-12 documents for integration. Runtime needs
no external JSON Schema validator; relational and temporal checks live in code.
retrieval.py, fixtures.py, pipeline.py, ingestion.sql and base/: Chapter 7 retrieval.
previous_solutions.py: previous exercises retained for regression tests.

PROFILE
1-3 questions of 1-400 characters; UTF-8 body no larger than 4096 bytes.
Exact application/json media type. request_id correlates, not authenticates or deduplicates.
accepted, progress, result, error, cancelled events; consecutive sequence 1..32.
Restricted SSE: three lines (event, id, data), LF separators, one-line JSON,
final blank line. At most 16384 bytes per frame and 131072 per stream.
No comments, CRLF, retry, multiline data, or EventSource resumption.
Not an HTTP server, general SSE parser, distributed system, or model client.
consume reads a finite stream; Client updates state on each frame.

complete/partial/no_answer describe coverage of independent questions.
Abstention and clarification carry neither answer text nor citations. Unexpected
failure discards the whole operation; it is not disguised as per-item abstention.
Cancellation is cooperative and checked at specific points. It neither refunds
work nor retracts delivered content. Access is rechecked before release, without
a proof of linearization spanning verification and network delivery.
No latency, load, LLM, proxy, socket, or real client benchmark was performed.
