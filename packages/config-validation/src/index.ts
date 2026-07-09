import { z } from "zod";

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
  features: z.object({
    enableReviews: z.boolean().default(true),
    enableInstalls: z.boolean().default(false),
    enableCustomQuote: z.boolean().default(false),
  }).default({}),
});

export type ThemeConfig = z.infer<typeof ThemeConfigSchema>;
export type IntegrationsConfig = z.infer<typeof IntegrationsConfigSchema>;
export type SiteConfig = z.infer<typeof SiteConfigSchema>;

export function validateSiteConfig(config: unknown): SiteConfig {
  return SiteConfigSchema.parse(config);
}
