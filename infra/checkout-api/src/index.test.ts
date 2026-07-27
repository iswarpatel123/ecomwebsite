import { describe, it, expect, vi, beforeEach } from "vitest";
import worker, { Env } from "./index.js";
import { CartItem } from "@dropshipping/core-commerce";

describe("Shared Checkout API Worker", () => {
  let mockEnv: Env;
  let mockCtx: any;

  beforeEach(() => {
    vi.restoreAllMocks();

    mockCtx = {
      waitUntil: vi.fn(),
      passThroughOnException: vi.fn(),
    };

    mockEnv = {
      STRIPE_SECRET_KEY: "mock_stripe_secret_key",
      STRIPE_WEBHOOK_SECRET: "mock_stripe_webhook_secret",
    };
  });

  describe("CORS and GET /health", () => {
    it("should return 204 for OPTIONS preflight", async () => {
      const request = new Request("https://checkout.example.com/checkout/session", {
        method: "OPTIONS",
        headers: {
          Origin: "https://my-storefront.pages.dev",
        },
      });

      const response = await worker.fetch(request, mockEnv, mockCtx);
      expect(response.status).toBe(204);
      expect(response.headers.get("Access-Control-Allow-Origin")).toBe("https://my-storefront.pages.dev");
      expect(response.headers.get("Access-Control-Allow-Methods")).toBe("GET, POST, OPTIONS");
    });

    it("should return 200 and status ok for GET /health", async () => {
      const request = new Request("https://checkout.example.com/health", {
        method: "GET",
      });

      const response = await worker.fetch(request, mockEnv, mockCtx);
      expect(response.status).toBe(200);
      const body = await response.json() as any;
      expect(body.status).toBe("ok");
      expect(body.service).toBe("shared-checkout-api");
    });
  });

  describe("POST /checkout/session", () => {
    const lineItems: CartItem[] = [
      {
        product: {
          id: "p1",
          name: "Modern Oak Dining Table",
          price: 799.00,
          sku: "FURN-OAK-TAB",
          niche: "furniture",
        },
        quantity: 1,
      }
    ];

    it("should return 400 if required parameters are missing", async () => {
      const request = new Request("https://checkout.example.com/checkout/session", {
        method: "POST",
        body: JSON.stringify({
          siteId: "site_furn_01",
          // missing lineItems
        }),
      });

      const response = await worker.fetch(request, mockEnv, mockCtx);
      expect(response.status).toBe(400);
      const body = await response.json() as any;
      expect(body.error).toBe("Missing required parameters");
    });

    it("should return a mock checkout session URL if Stripe key is mock", async () => {
      const request = new Request("https://checkout.example.com/checkout/session", {
        method: "POST",
        body: JSON.stringify({
          siteId: "site_furn_01",
          lineItems,
          successUrl: "https://my-storefront.pages.dev/success",
          cancelUrl: "https://my-storefront.pages.dev/cancel",
        }),
      });

      const response = await worker.fetch(request, mockEnv, mockCtx);
      expect(response.status).toBe(200);
      const body = await response.json() as any;
      expect(body.url).toContain("https://my-storefront.pages.dev/success");
      expect(body.url).toContain("session_id=cs_mock_");
      expect(body.orderId).toBeDefined();
      expect(body.mock).toBe(true);
    });

    it("should invoke real Stripe API if STRIPE_SECRET_KEY is a real key", async () => {
      mockEnv.STRIPE_SECRET_KEY = "sk_live_real_stripe_key_123456";

      const mockStripeResponse = {
        url: "https://checkout.stripe.com/c/pay/cs_live_real_session_xyz",
      };

      const globalFetchSpy = vi.spyOn(globalThis, "fetch").mockImplementation(async (url) => {
        if (url === "https://api.stripe.com/v1/checkout/sessions") {
          return new Response(JSON.stringify(mockStripeResponse), { status: 200 });
        }
        return new Response(null, { status: 404 });
      });

      const request = new Request("https://checkout.example.com/checkout/session", {
        method: "POST",
        body: JSON.stringify({
          siteId: "site_furn_01",
          lineItems,
          successUrl: "https://my-storefront.pages.dev/success",
          cancelUrl: "https://my-storefront.pages.dev/cancel",
        }),
      });

      const response = await worker.fetch(request, mockEnv, mockCtx);
      expect(response.status).toBe(200);
      const body = await response.json() as any;
      expect(body.url).toBe("https://checkout.stripe.com/c/pay/cs_live_real_session_xyz");
      expect(body.orderId).toBeDefined();

      expect(globalFetchSpy).toHaveBeenCalledTimes(1);
    });

    it("should pre-insert the pending order into D1 if DB is bound", async () => {
      const mockFirst = vi.fn().mockResolvedValue({ tenant_id: "tenant_cozy_living" });
      const mockRun = vi.fn().mockResolvedValue({ success: true });
      const mockPrepare = vi.fn().mockReturnValue({
        bind: vi.fn().mockReturnValue({
          first: mockFirst,
          run: mockRun,
        }),
      });

      mockEnv.DB = {
        prepare: mockPrepare,
      } as any;

      const request = new Request("https://checkout.example.com/checkout/session", {
        method: "POST",
        body: JSON.stringify({
          siteId: "site_furn_01",
          lineItems,
          successUrl: "https://my-storefront.pages.dev/success",
          cancelUrl: "https://my-storefront.pages.dev/cancel",
        }),
      });

      const response = await worker.fetch(request, mockEnv, mockCtx);
      expect(response.status).toBe(200);

      // Verify that DB prepare was called
      expect(mockPrepare).toHaveBeenCalled();
    });
  });

  describe("POST /webhooks/stripe", () => {
    it("should handle checkout.session.completed and record order to D1", async () => {
      const mockFirst = vi.fn().mockResolvedValue({ id: "ord_1234" });
      const mockRun = vi.fn().mockResolvedValue({ success: true });
      const mockPrepare = vi.fn().mockReturnValue({
        bind: vi.fn().mockReturnValue({
          first: mockFirst,
          run: mockRun,
        }),
      });

      mockEnv.DB = {
        prepare: mockPrepare,
      } as any;

      const stripeWebhookPayload = {
        type: "checkout.session.completed",
        data: {
          object: {
            id: "cs_test_123",
            payment_intent: "pi_test_123",
            amount_subtotal: 79900,
            amount_total: 86292,
            total_details: {
              amount_tax: 6392,
              amount_shipping: 0,
            },
            customer_details: {
              email: "customer@example.com",
              name: "Jane Doe",
              address: {
                line1: "123 Main St",
                city: "Sydney",
                state: "NSW",
                postal_code: "2000",
                country: "AU",
              },
            },
            metadata: {
              siteId: "site_furn_01",
              tenantId: "tenant_cozy_living",
              orderId: "ord_1234",
            },
          },
        },
      };

      const request = new Request("https://checkout.example.com/webhooks/stripe", {
        method: "POST",
        body: JSON.stringify(stripeWebhookPayload),
      });

      const response = await worker.fetch(request, mockEnv, mockCtx);
      expect(response.status).toBe(200);
      const body = await response.json() as any;
      expect(body.received).toBe(true);

      // Should check if order exists first and update it
      expect(mockPrepare).toHaveBeenCalled();
    });
  });
});
