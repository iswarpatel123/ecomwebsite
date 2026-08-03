CREATE TABLE IF NOT EXISTS meta_dataset_registry (
  site_id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  canonical_origin TEXT NOT NULL UNIQUE,
  dataset_mode TEXT NOT NULL CHECK (dataset_mode IN ('per_site', 'shared')),
  pixel_id TEXT NOT NULL,
  dataset_id TEXT NOT NULL,
  capi_route_key TEXT NOT NULL UNIQUE,
  active INTEGER NOT NULL DEFAULT 1,
  shared_dataset_key TEXT,
  approval_json TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (site_id) REFERENCES sites(id) ON DELETE CASCADE,
  FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS meta_event_ledger (
  site_id TEXT NOT NULL,
  event_id TEXT NOT NULL,
  event_name TEXT NOT NULL,
  dataset_id TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('pending', 'sent', 'retry', 'dead_letter')),
  attempts INTEGER NOT NULL DEFAULT 0,
  meta_event_id TEXT,
  payload_hash TEXT,
  last_error TEXT,
  next_attempt_at DATETIME,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (site_id, event_id, event_name),
  FOREIGN KEY (site_id) REFERENCES sites(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_meta_ledger_status ON meta_event_ledger(status, next_attempt_at);
