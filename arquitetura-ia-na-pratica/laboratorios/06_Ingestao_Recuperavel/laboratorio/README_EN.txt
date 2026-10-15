CHAPTER 6 LAB — RECOVERABLE INGESTION
Python 3.10+ with sqlite3. Standard library only. Fictional data.
The validated runtime is recorded in ../Verificacao.json.
From laboratorio, run:
python -m unittest discover -v
python scenarios.py
python solutions.py

41 tests; 12 scenarios; solved exercises 11 and 12. The last two commands
write results/. Exercise 11 creates a temporary database under this
directory and removes it afterward. A writable directory is required.
source.json is a readable copy of the texts in scenarios.py; executable
scenarios use SOURCE from that module. To experiment with the file,
pass Path('source.json').read_bytes() as the raw argument.

base/store.py and base/schema.sql are unchanged Chapter 5 copies.
Pipeline uses the same repository and Copilot. This is not an HTTP server.
Administrative methods require a trusted caller. Time is logical.
No network, model, translation, OCR, or embedding calls are made.

OBSERVED GUARANTEES
Atomic batches and cursors; restart using a new connection; token fencing;
complete activation with manifest, version, and epoch checks; authorized
reads that refuse during projection lag; purge of deleted documents'
staging. Repeated activation acknowledges a historical publication.

LIMITS
Bilingual UTF-8 JSON up to 8192 bytes, 6000 characters per language.
Character windows, not tokens; examples do not measure RAG quality.
Three acquisitions per job; no backoff, jitter, or real scheduler.
Local single-writer SQLite, not a distributed concurrency proof.
Trusted test clock and small parser inside the transaction.
No global quotas, sandbox, HTTP authentication, or external vector index.
Orphan quarantines need another collector. Purge does not erase backups,
remote caches, or physical database pages. A manifest is not a signature.
