R04 ENGLISH EDITION
English entry points select en-US explicitly. Original bilingual fixtures
and Portuguese entry points remain unchanged. See ENGLISH_EDITION_R04.txt.

CHAPTER 5 - DATA, VERSIONS, AND PERMISSIONS
Rodrigo Sillos | Tecnologia na Prática | October 14, 2026 | R01

Requires Python 3.10+ with sqlite3. Verified on Python 3.12.14.
No extra dependencies, credentials, network, or paid models.
From the laboratorio folder, run:

python -m unittest discover -v
python scenarios_en.py
python solutions_en.py

Expected: 32 passing tests, 12/12 observations, and Exercises 9 and 10
without assertion failures. scenarios_en.py replaces results/scenarios.json.
Copy your reports before rerunning if you need to preserve comparisons.

FILES
schema.sql: eight tables with tenant-scoped identities and relationships.
store.py: publication, authorization, projection, cache, and deletion.
scenarios_en.py: fictional data, controlled transitions, and report.
solutions_en.py: interrupted publication; revocation and purge.
test_store.py: behavior checks, including two connections.
results/: observed and verified outputs included with the delivery.

Scenarios use an in-memory database. The two-connection test creates a
temporary file inside this folder, closes connections, and removes its
temporary files on completion. No external database is accessed.

MAIN RESULTS
Acme and Zen share a doc_id but have different text.
Alice belongs to Acme; Bob belongs to Zen. Alice has no Zen membership.
New revision: reads block until the projection catches up.
Old event: the consumer reads current state; it cannot roll back a version.
Revocation between preparation and delivery blocks the response.
Deletion on logical day 10 with 2 teaching retention days: purge on day 12.

EXERCISES
9: inject a failure before commit; check rollback; retry the same command
key; observe version 2 with no duplicate publication.
10: fill cache; revoke during a request; delete; replay an old event;
verify the purge boundary and explicitly clear local cache.

LIMITS
Actor is a trusted fixture; authentication and administrative HTTP APIs
are not implemented. Write methods require a trusted caller.
Copilot is an extractive stand-in, without an LLM, embeddings, or semantic
retrieval. It is not a ready integration with Chapter 3's HTTP server.
It continues the repository responsibility and Chapter 4's negative cases.
Index and outbox share a local transaction; there is no external queue.
The two-connection test is not a load test or a proof of concurrency.
Snapshot checks happen before delivery, without atomicity with network
or streaming. Revocation after the final check is not covered.
Versions are immutable through the offered API, not against administrative
SQL. Hashing does not authenticate authorship. ACLs are current, not historical.
Purge removes version, ACL, and projection rows. Tombstones, events, and
command records remain. RAM cache requires separate cleanup.
There is no secure erasure of disk, backups, logs, or external copies.
The 2-day logical interval is a teaching value, not legal retention advice.
