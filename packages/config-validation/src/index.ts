import { z } from "zod";

const NumericIdSchema = z.string().regex(/^\d+$/, "Meta IDs must contain only digits");

export const MetaConfigSchema = z.object({
  enabled: z.boolean().default(false),
  dataset_mode: z.enum(["per_site", "shared"]).default("per_site"),
  pixel_id: NumericIdSchema.optional(),
  dataset_id: NumericIdSchema.optional(),
  capi_route_key: z.string().min(1).optional(),
  shared_dataset_key: z.string().min(1).optional(),
  test_event_code: z.string().min(1).nullable().optional(),
  send_browser_events: z.boolean().default(true),
  send_server_events: z.boolean().default(false),
  consent_required: z.boolean().default(true),
  checkout_endpoint: z.string().url().optional(),
}).superRefine((meta, ctx) => {
  if (meta.enabled && !meta.pixel_id) {
    ctx.addIssue({ code: z.ZodIssueCode.custom, path: ["pixel_id"], message: "Enabled Meta integration requires pixel_id" });
  }
  if (meta.dataset_mode === "per_site" && meta.enabled && !meta.dataset_id) {
    ctx.addIssue({ code: z.ZodIssueCode.custom, path: ["dataset_id"], message: "Per-site Meta integration requires dataset_id or pixel_id" });
  }
  if (meta.dataset_mode === "shared" && !meta.shared_dataset_key) {
    ctx.addIssue({ code: z.ZodIssueCode.custom, path: ["shared_dataset_key"], message: "Shared Meta integration requires shared_dataset_key" });
  }
});

export const AnalyticsConfigSchema = z.object({
  meta: MetaConfigSchema.default({}),
});

// Shared Theme configuration schema
export const ThemeConfigSchema = z.object({
  primaryColor: z.string().default("#3b82f6"),
  secondaryColor: z.string().default("#1f2937"),
  fontFamily: z.string().default("sans-serif"),
  logoUrl: z.string().url().optional(),
});

// Shared Integration details (Stripe, Analytics, Braintree, etc.)
export const IntegrationsConfigSchema = z.object({
  stripePublishableKey: z.string().min(1, "Stripe key is required"),
  googleAnalyticsId: z.string().optional(),
  braintreeTokenizationKey: z.string().optional(),
});

// Full Multi-tenant Site Configuration schema
export const SiteConfigSchema = z.object({
  siteId: z.string(),
  tenantId: z.string(),
  domain: z.string(),
  siteName: z.string(),
  niche: z.enum(["furniture", "saunas", "grills"]),
  theme: ThemeConfigSchema,
  integrations: IntegrationsConfigSchema,
  analytics: AnalyticsConfigSchema.default({}),
  features: z.object({
    enableReviews: z.boolean().default(true),
    enableInstalls: z.boolean().default(false),
    enableCustomQuote: z.boolean().default(false),
  }).default({}),
});

export type ThemeConfig = z.infer<typeof ThemeConfigSchema>;
export type IntegrationsConfig = z.infer<typeof IntegrationsConfigSchema>;
export type MetaConfig = z.infer<typeof MetaConfigSchema>;
export type AnalyticsConfig = z.infer<typeof AnalyticsConfigSchema>;
export type SiteConfig = z.infer<typeof SiteConfigSchema>;

export function validateSiteConfig(config: unknown): SiteConfig {
  return SiteConfigSchema.parse(config);
}
