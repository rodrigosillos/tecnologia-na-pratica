CREATE TABLE IF NOT EXISTS jobs (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 tenant TEXT NOT NULL, subject TEXT NOT NULL,
 operation TEXT NOT NULL, idem_key TEXT NOT NULL,
 fingerprint TEXT NOT NULL, payload TEXT NOT NULL,
 state TEXT NOT NULL CHECK(state IN
 ('queued','running','retry_wait','succeeded','failed','cancelled','expired')),
 created_ms INTEGER NOT NULL, deadline_ms INTEGER NOT NULL,
 next_ms INTEGER NOT NULL, attempts INTEGER NOT NULL DEFAULT 0,
 generation INTEGER NOT NULL DEFAULT 0, worker TEXT,
 lease_until INTEGER NOT NULL DEFAULT 0,
 stage INTEGER NOT NULL DEFAULT 0 CHECK(stage BETWEEN 0 AND 2),
 cancel_requested INTEGER NOT NULL DEFAULT 0,
 error_code TEXT,
 UNIQUE(tenant,subject,operation,idem_key)
);
CREATE TABLE IF NOT EXISTS dispatch_outbox (
 event_id INTEGER PRIMARY KEY AUTOINCREMENT,
 job_id INTEGER NOT NULL UNIQUE REFERENCES jobs(id),
 sent INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS checkpoints (
 job_id INTEGER NOT NULL REFERENCES jobs(id),
 position INTEGER NOT NULL CHECK(position IN (0,1)),
 value TEXT NOT NULL, PRIMARY KEY(job_id,position)
);
CREATE TABLE IF NOT EXISTS job_results (
 job_id INTEGER PRIMARY KEY REFERENCES jobs(id), value TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS dead_letters (
 job_id INTEGER PRIMARY KEY REFERENCES jobs(id),
 reason TEXT NOT NULL, attempts INTEGER NOT NULL
);
