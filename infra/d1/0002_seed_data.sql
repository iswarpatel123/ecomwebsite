-- Migration 0002: Seed Data for Testing Niche Deployments

INSERT INTO tenants (id, name, email, status) VALUES
('tenant_cozy_living', 'Cozy Living Co.', 'billing@cozyliving.example.com', 'active'),
('tenant_nordic_glow', 'Nordic Glow Saunas', 'support@nordicglow.example.com', 'active');

INSERT INTO sites (id, tenant_id, domain, site_name, niche, config_json) VALUES
('site_furn_01', 'tenant_cozy_living', 'cozy-furniture.example.com', 'Cozy Furniture Niche Hub', 'furniture', '{
  "siteId": "site_furn_01",
  "tenantId": "tenant_cozy_living",
  "domain": "cozy-furniture.example.com",
  "siteName": "Cozy Furniture Niche Hub",
  "niche": "furniture",
  "theme": {
    "primaryColor": "#4f46e5",
    "secondaryColor": "#111827",
    "fontFamily": "sans-serif"
  },
  "integrations": {
    "stripePublishableKey": "pk_test_furniture_key_123",
    "googleAnalyticsId": "UA-FURN-MOCK"
  },
  "features": {
    "enableReviews": true,
    "enableInstalls": true,
    "enableCustomQuote": false
  }
}'),
('site_sauna_99', 'tenant_nordic_glow', 'nordic-glow-saunas.example.com', 'Nordic Glow Luxury Saunas', 'saunas', '{
  "siteId": "site_sauna_99",
  "tenantId": "tenant_nordic_glow",
  "domain": "nordic-glow-saunas.example.com",
  "siteName": "Nordic Glow Luxury Saunas",
  "niche": "saunas",
  "theme": {
    "primaryColor": "#78350f",
    "secondaryColor": "#451a03",
    "fontFamily": "serif"
  },
  "integrations": {
    "stripePublishableKey": "pk_test_saunas_braintree_fallback",
    "braintreeTokenizationKey": "bt_tok_nordic_saunas_99"
  },
  "features": {
    "enableReviews": true,
    "enableInstalls": true,
    "enableCustomQuote": true
  }
}');

INSERT INTO products (id, site_id, name, sku, price, cost_price, inventory_count, image_url, description, metadata_json) VALUES
('p1', 'site_furn_01', 'Modern Oak Dining Table', 'FURN-OAK-TAB', 799.00, 420.00, -1, 'https://assets.example.com/images/oak-table.jpg', 'Beautifully crafted dining table from natural oakwood.', '{"weightKg": 45, "assemblyRequired": true}'),
('p2', 'site_furn_01', 'Ergonomic Office Chair', 'FURN-ERG-CHR', 249.50, 110.00, -1, 'https://assets.example.com/images/erg-chair.jpg', 'Adjustable office seating with lumber support.', '{"colors": ["black", "grey", "white"]}'),
('p3', 'site_furn_01', 'Velvet Chesterfield Sofa', 'FURN-VLV-SOF', 1299.00, 680.00, -1, 'https://assets.example.com/images/velvet-sofa.jpg', 'Luxurious chesterfield velvet upholstered sofa.', '{"weightKg": 95, "shippingClass": "freight"}'),
('s1', 'site_sauna_99', 'Nordic Outdoor Barrel Sauna (4-Person)', 'SAUN-BAR-4P', 5499.00, 3100.00, -1, 'https://assets.example.com/images/barrel-sauna.jpg', 'Authentic Western Red Cedar outdoor barrel sauna.', '{"woodOption": "cedar", "capacity": 4}'),
('s2', 'site_sauna_99', 'Indoor Far-Infrared Cabin', 'SAUN-INF-CAB', 3899.00, 2200.00, -1, 'https://assets.example.com/images/infrared-cabin.jpg', 'Modern infrared elements with carbon-fiber emitters.', '{"heatersCount": 6, "capacity": 2}'),
('s3', 'site_sauna_99', 'Traditional Finnish Sauna Heater (9kW)', 'SAUN-HTR-9KW', 899.00, 450.00, -1, 'https://assets.example.com/images/heater-9kw.jpg', 'Premium stainless steel wall-mounted sauna electric stove.', '{"voltage": "240v"}');
