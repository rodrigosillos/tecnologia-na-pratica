PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS epochs (
  tenant TEXT PRIMARY KEY, epoch INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS principals (
  tenant TEXT NOT NULL, user_id TEXT NOT NULL,
  role TEXT NOT NULL, active INTEGER NOT NULL CHECK(active IN (0,1)),
  PRIMARY KEY(tenant,user_id)
);
CREATE TABLE IF NOT EXISTS documents (
  tenant TEXT NOT NULL, doc_id TEXT NOT NULL,
  active_version INTEGER NOT NULL, seq INTEGER NOT NULL,
  deleted INTEGER NOT NULL DEFAULT 0 CHECK(deleted IN (0,1)),
  purge_at INTEGER, PRIMARY KEY(tenant,doc_id)
);
CREATE TABLE IF NOT EXISTS versions (
  tenant TEXT NOT NULL, doc_id TEXT NOT NULL, version INTEGER NOT NULL,
  body_pt TEXT NOT NULL, body_en TEXT NOT NULL,
  source_uri TEXT NOT NULL, digest TEXT NOT NULL,
  PRIMARY KEY(tenant,doc_id,version),
  FOREIGN KEY(tenant,doc_id) REFERENCES documents(tenant,doc_id)
);
CREATE TABLE IF NOT EXISTS acl (
  tenant TEXT NOT NULL, doc_id TEXT NOT NULL, role TEXT NOT NULL,
  PRIMARY KEY(tenant,doc_id,role),
  FOREIGN KEY(tenant,doc_id) REFERENCES documents(tenant,doc_id)
);
CREATE TABLE IF NOT EXISTS outbox (
  event_id INTEGER PRIMARY KEY AUTOINCREMENT,
  tenant TEXT NOT NULL, doc_id TEXT NOT NULL, seq INTEGER NOT NULL,
  done INTEGER NOT NULL DEFAULT 0 CHECK(done IN (0,1)),
  FOREIGN KEY(tenant,doc_id) REFERENCES documents(tenant,doc_id)
);
CREATE TABLE IF NOT EXISTS projection (
  tenant TEXT NOT NULL, doc_id TEXT NOT NULL,
  version INTEGER NOT NULL, seq INTEGER NOT NULL, digest TEXT NOT NULL,
  PRIMARY KEY(tenant,doc_id),
  FOREIGN KEY(tenant,doc_id) REFERENCES documents(tenant,doc_id)
);
CREATE TABLE IF NOT EXISTS commands (
  tenant TEXT NOT NULL, request_id TEXT NOT NULL,
  payload_hash TEXT NOT NULL, result_version INTEGER NOT NULL,
  PRIMARY KEY(tenant,request_id)
);
