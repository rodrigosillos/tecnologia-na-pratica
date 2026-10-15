CREATE TABLE IF NOT EXISTS jobs (
 job_id TEXT PRIMARY KEY, tenant TEXT NOT NULL, doc_id TEXT NOT NULL,
 request_id TEXT NOT NULL, payload_hash TEXT NOT NULL,
 raw BLOB NOT NULL, raw_hash TEXT NOT NULL, source_uri TEXT NOT NULL,
 roles TEXT NOT NULL, expected INTEGER NOT NULL, base_epoch INTEGER NOT NULL,
 config TEXT NOT NULL, state TEXT NOT NULL DEFAULT 'queued',
 owner TEXT, token INTEGER NOT NULL DEFAULT 0, lease_until INTEGER,
 claims INTEGER NOT NULL DEFAULT 0, normalized TEXT,
 total INTEGER NOT NULL DEFAULT 0, cursor INTEGER NOT NULL DEFAULT 0,
 manifest TEXT, result_version INTEGER, error TEXT,
 UNIQUE(tenant,request_id),
 CHECK(state IN ('queued','staging','ready','published','quarantined','obsolete'))
);
CREATE TABLE IF NOT EXISTS chunks (
 job_id TEXT NOT NULL REFERENCES jobs(job_id),
 language TEXT NOT NULL, ordinal INTEGER NOT NULL,
 start INTEGER NOT NULL, stop INTEGER NOT NULL,
 body TEXT NOT NULL, digest TEXT NOT NULL, chunk_id TEXT NOT NULL UNIQUE,
 PRIMARY KEY(job_id,language,ordinal)
);
CREATE TABLE IF NOT EXISTS heads (
 tenant TEXT NOT NULL, doc_id TEXT NOT NULL,
 job_id TEXT NOT NULL REFERENCES jobs(job_id), version INTEGER NOT NULL,
 PRIMARY KEY(tenant,doc_id),
 FOREIGN KEY(tenant,doc_id) REFERENCES documents(tenant,doc_id)
);
