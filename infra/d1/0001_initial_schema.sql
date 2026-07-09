-- Migration 0001: Initial Schema for multi-tenant dropshipping/reselling platform
-- Cloudflare D1 SQL Schema Definitions

CREATE TABLE IF NOT EXISTS tenants (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT NOT NULL UNIQUE,
  status TEXT DEFAULT 'active' CHECK (status IN ('active', 'suspended', 'inactive')),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sites (
  id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  domain TEXT NOT NULL UNIQUE,
  site_name TEXT NOT NULL,
  niche TEXT NOT NULL CHECK (niche IN ('furniture', 'saunas', 'grills')),
  config_json TEXT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS products (
  id TEXT PRIMARY KEY,
  site_id TEXT NOT NULL,
  name TEXT NOT NULL,
  sku TEXT NOT NULL,
  price REAL NOT NULL,
  cost_price REAL,
  inventory_count INTEGER DEFAULT -1,
  image_url TEXT,
  description TEXT,
  metadata_json TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (site_id) REFERENCES sites(id) ON DELETE CASCADE,
  UNIQUE(site_id, sku)
);

CREATE TABLE IF NOT EXISTS orders (
  id TEXT PRIMARY KEY,
  site_id TEXT NOT NULL,
  tenant_id TEXT NOT NULL,
  stripe_charge_id TEXT,
  braintree_transaction_id TEXT,
  subtotal REAL NOT NULL,
  tax REAL NOT NULL,
  shipping REAL NOT NULL,
  total REAL NOT NULL,
  customer_email TEXT NOT NULL,
  customer_first_name TEXT NOT NULL,
  customer_last_name TEXT NOT NULL,
  shipping_address_json TEXT NOT NULL,
  status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'paid', 'shipped', 'cancelled')),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (site_id) REFERENCES sites(id),
  FOREIGN KEY (tenant_id) REFERENCES tenants(id)
);

CREATE INDEX IF NOT EXISTS idx_sites_tenant ON sites(tenant_id);
CREATE INDEX IF NOT EXISTS idx_sites_domain ON sites(domain);
CREATE INDEX IF NOT EXISTS idx_products_site ON products(site_id);
CREATE INDEX IF NOT EXISTS idx_orders_site ON orders(site_id);
