import { calculateCart, CartItem } from "@dropshipping/core-commerce";

export interface Env {
  DB?: D1Database;
  STRIPE_SECRET_KEY?: string;
  STRIPE_WEBHOOK_SECRET?: string;
  META_CAPI_ACCESS_TOKEN?: string;
  META_GRAPH_API_VERSION?: string;
}

const fallbackTenantMap: Record<string, string> = {
  "site_furn_01": "tenant_cozy_living",
  "site_sauna_99": "tenant_nordic_glow",
};

function getCorsHeaders(request: Request): HeadersInit {
  const origin = request.headers.get("Origin") || "*";
  return {
    "Access-Control-Allow-Origin": origin,
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Stripe-Signature",
    "Access-Control-Allow-Credentials": "true",
    "Access-Control-Max-Age": "86400",
  };
}

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const corsHeaders = getCorsHeaders(request);

    // Handle OPTIONS preflight request
    if (request.method === "OPTIONS") {
      return new Response(null, {
        status: 204,
        headers: corsHeaders,
      });
    }

    const url = new URL(request.url);

    // GET /health
    if (request.method === "GET" && (url.pathname === "/" || url.pathname === "/health")) {
      return new Response(JSON.stringify({ status: "ok", service: "shared-checkout-api" }), {
        status: 200,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    // POST /checkout/session
    if (request.method === "POST" && url.pathname === "/checkout/session") {
      try {
        const body = await request.json() as {
          siteId: string;
          lineItems: CartItem[];
          successUrl: string;
          cancelUrl: string;
          shippingRate?: number;
          taxRate?: number;
          checkoutEventId?: string;
          fbp?: string;
          fbc?: string;
          eventSourceUrl?: string;
        };

        const { siteId, lineItems, successUrl, cancelUrl, shippingRate = 0, taxRate = 0.08, checkoutEventId, fbp, fbc, eventSourceUrl } = body;

        if (!siteId || !lineItems || !Array.isArray(lineItems) || !successUrl || !cancelUrl) {
          return new Response(JSON.stringify({ error: "Missing required parameters" }), {
            status: 400,
            headers: { ...corsHeaders, "Content-Type": "application/json" },
          });
        }
        if (env.DB) {
          const registry = await env.DB.prepare(
            "SELECT site_id FROM meta_dataset_registry WHERE site_id = ? AND active = 1"
          ).bind(siteId).first();
          if (!registry) {
            return new Response(JSON.stringify({ error: "Unknown or inactive site" }), {
              status: 400, headers: { ...corsHeaders, "Content-Type": "application/json" },
            });
          }
        }

        // Get tenant ID from D1 or fallback
        let tenantId = fallbackTenantMap[siteId] || "unknown";
        if (env.DB) {
          try {
            const siteRow = await env.DB.prepare(
              "SELECT tenant_id FROM sites WHERE id = ?"
            ).bind(siteId).first<{ tenant_id: string }>();
            if (siteRow) {
              tenantId = siteRow.tenant_id;
            }
          } catch (e) {
            console.error("D1 site query error:", e);
          }
        }

        // Calculate checkout totals
        const cart = calculateCart(lineItems, shippingRate, taxRate);
        const orderId = `ord_${Math.random().toString(36).substring(2, 9)}`;

        // If D1 is bound, pre-insert order in pending state
        if (env.DB) {
          try {
            await env.DB.prepare(
              `INSERT INTO orders (
                id, site_id, tenant_id, subtotal, tax, shipping, total,
                customer_email, customer_first_name, customer_last_name, shipping_address_json, status
              ) VALUES (?, ?, ?, ?, ?, ?, ?, 'pending@example.com', 'Pending', 'Customer', '{}', 'pending')`
            ).bind(
              orderId,
              siteId,
              tenantId,
              cart.subtotal,
              cart.tax,
              cart.shipping,
              cart.total
            ).run();
            if (checkoutEventId) {
              await env.DB.prepare(
                "UPDATE orders SET checkout_event_id = ?, fbp = ?, fbc = ?, event_source_url = ? WHERE id = ?"
              ).bind(checkoutEventId, fbp || null, fbc || null, eventSourceUrl || null, orderId).run();
            }
          } catch (e) {
            console.error("D1 order pre-insert error:", e);
          }
        }

        const isRealStripe = env.STRIPE_SECRET_KEY && !env.STRIPE_SECRET_KEY.startsWith("mock_");

        if (isRealStripe) {
          // Stripe requires amounts in cents
          const stripeBody = new URLSearchParams();
          stripeBody.append("success_url", successUrl);
          stripeBody.append("cancel_url", cancelUrl);
          stripeBody.append("mode", "payment");
          stripeBody.append("metadata[siteId]", siteId);
          stripeBody.append("metadata[tenantId]", tenantId);
          stripeBody.append("metadata[orderId]", orderId);

          lineItems.forEach((item, index) => {
            const unitAmount = Math.round(item.product.price * 100);
            stripeBody.append(`line_items[${index}][price_data][currency]`, "usd");
            stripeBody.append(`line_items[${index}][price_data][unit_amount]`, String(unitAmount));
            stripeBody.append(`line_items[${index}][price_data][product_data][name]`, item.product.name);
            stripeBody.append(`line_items[${index}][price_data][product_data][metadata][sku]`, item.product.sku);
            stripeBody.append(`line_items[${index}][price_data][product_data][metadata][id]`, item.product.id);
            stripeBody.append(`line_items[${index}][quantity]`, String(item.quantity));
          });

          // Add shipping/tax details to Stripe checkout if appropriate
          if (cart.shipping > 0) {
            stripeBody.append("shipping_options[0][shipping_rate_data][type]", "fixed_amount");
            stripeBody.append("shipping_options[0][shipping_rate_data][fixed_amount][amount]", String(Math.round(cart.shipping * 100)));
            stripeBody.append("shipping_options[0][shipping_rate_data][fixed_amount][currency]", "usd");
            stripeBody.append("shipping_options[0][shipping_rate_data][display_name]", "Shipping");
          }

          const stripeResponse = await fetch("https://api.stripe.com/v1/checkout/sessions", {
            method: "POST",
            headers: {
              "Authorization": `Bearer ${env.STRIPE_SECRET_KEY}`,
              "Content-Type": "application/x-www-form-urlencoded",
            },
            body: stripeBody.toString(),
          });

          if (!stripeResponse.ok) {
            const errorText = await stripeResponse.text();
            console.error("Stripe Checkout Session creation failed:", errorText);
            throw new Error(`Stripe API error: ${errorText}`);
          }

          const stripeSession = await stripeResponse.json() as { url: string };
          return new Response(JSON.stringify({ url: stripeSession.url, orderId }), {
            status: 200,
            headers: { ...corsHeaders, "Content-Type": "application/json" },
          });
        } else {
          // Mock Flow
          const mockSessionId = `cs_mock_${Math.random().toString(36).substring(2, 10)}`;
          // We provide a success URL redirect with mock session parameters
          const mockCheckoutUrl = `${successUrl}?session_id=${mockSessionId}&order_id=${orderId}`;

          return new Response(JSON.stringify({ url: mockCheckoutUrl, orderId, mock: true }), {
            status: 200,
            headers: { ...corsHeaders, "Content-Type": "application/json" },
          });
        }
      } catch (e: any) {
        return new Response(JSON.stringify({ error: e.message || "Internal Server Error" }), {
          status: 500,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        });
      }
    }

    // POST /webhooks/stripe
    if (request.method === "POST" && url.pathname === "/webhooks/stripe") {
      try {
        const rawBody = await request.text();
        const signatureHeader = request.headers.get("Stripe-Signature");

        const isRealWebhook = env.STRIPE_WEBHOOK_SECRET && !env.STRIPE_WEBHOOK_SECRET.startsWith("mock_");

        if (isRealWebhook) {
          if (!signatureHeader) {
            return new Response(JSON.stringify({ error: "Missing Stripe-Signature header" }), {
              status: 400,
              headers: { ...corsHeaders, "Content-Type": "application/json" },
            });
          }

          const isValid = await verifyStripeSignature(rawBody, signatureHeader, env.STRIPE_WEBHOOK_SECRET!);
          if (!isValid) {
            return new Response(JSON.stringify({ error: "Invalid Stripe Signature" }), {
              status: 400,
              headers: { ...corsHeaders, "Content-Type": "application/json" },
            });
          }
        }

        const stripeEvent = JSON.parse(rawBody) as {
          type: string;
          data: {
            object: any;
          };
        };

        if (stripeEvent.type === "checkout.session.completed") {
          const session = stripeEvent.data.object;
          const orderId = session.metadata?.orderId;
          const siteId = session.metadata?.siteId || "unknown";
          const tenantId = session.metadata?.tenantId || fallbackTenantMap[siteId] || "unknown";
          const stripeChargeId = session.payment_intent || session.id;
          const checkoutEventId = session.metadata?.checkoutEventId || orderId || stripeChargeId;

          const subtotal = (session.amount_subtotal ?? 0) / 100;
          const tax = (session.total_details?.amount_tax ?? 0) / 100;
          const shipping = (session.total_details?.amount_shipping ?? 0) / 100;
          const total = (session.amount_total ?? 0) / 100;

          const customerEmail = session.customer_details?.email || "unknown@example.com";
          const customerName = session.customer_details?.name || "Anonymous Customer";
          const [firstName, ...lastNameParts] = customerName.split(" ");
          const lastName = lastNameParts.join(" ") || "Customer";

          const shippingAddress = session.shipping_details?.address || session.customer_details?.address || {};

          if (env.DB) {
            // Upsert / update the order
            let existingOrder = null;
            if (orderId) {
              existingOrder = await env.DB.prepare("SELECT id FROM orders WHERE id = ?").bind(orderId).first();
            }

            if (existingOrder) {
              await env.DB.prepare(
                `UPDATE orders SET
                  stripe_charge_id = ?,
                  subtotal = ?,
                  tax = ?,
                  shipping = ?,
                  total = ?,
                  customer_email = ?,
                  customer_first_name = ?,
                  customer_last_name = ?,
                  shipping_address_json = ?,
                  status = 'paid'
                WHERE id = ?`
              ).bind(
                stripeChargeId,
                subtotal,
                tax,
                shipping,
                total,
                customerEmail,
                firstName,
                lastName,
                JSON.stringify(shippingAddress),
                orderId
              ).run();
            } else {
              const newOrderId = orderId || `ord_${Math.random().toString(36).substring(2, 9)}`;
              await env.DB.prepare(
                `INSERT INTO orders (
                  id, site_id, tenant_id, stripe_charge_id, subtotal, tax, shipping, total,
                  customer_email, customer_first_name, customer_last_name, shipping_address_json, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'paid')`
              ).bind(
                newOrderId,
                siteId,
                tenantId,
                stripeChargeId,
                subtotal,
                tax,
                shipping,
                total,
                customerEmail,
                firstName,
                lastName,
                JSON.stringify(shippingAddress)
              ).run();
            }
          } else {
            console.log("No D1 database bound. Simulating order storage:", {
              orderId,
              siteId,
              tenantId,
              stripeChargeId,
              subtotal,
              tax,
              shipping,
              total,
              customerEmail,
              customerName,
              shippingAddress,
            });
          }
          if (env.DB && env.META_CAPI_ACCESS_TOKEN && orderId) {
            await sendPurchase(env, siteId, checkoutEventId, {
              orderId,
              value: total,
              currency: session.currency || "usd",
              email: customerEmail,
              fbp: session.metadata?.fbp,
              fbc: session.metadata?.fbc,
              eventSourceUrl: session.metadata?.eventSourceUrl,
            });
          }
        }

        return new Response(JSON.stringify({ received: true }), {
          status: 200,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        });
      } catch (e: any) {
        return new Response(JSON.stringify({ error: e.message || "Webhook processing failed" }), {
          status: 500,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        });
      }
    }

    return new Response(JSON.stringify({ error: "Not Found" }), {
      status: 404,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }
};

async function verifyStripeSignature(
  rawBody: string,
  signatureHeader: string,
  secret: string
): Promise<boolean> {
  try {
    const parts = signatureHeader.split(",");
    const tPart = parts.find(p => p.startsWith("t="));
    const v1Part = parts.find(p => p.startsWith("v1="));
    if (!tPart || !v1Part) return false;

    const timestamp = tPart.split("=")[1];
    const signature = v1Part.split("=")[1];

    const payload = `${timestamp}.${rawBody}`;

    const encoder = new TextEncoder();
    const key = await crypto.subtle.importKey(
      "raw",
      encoder.encode(secret),
      { name: "HMAC", hash: "SHA-256" },
      false,
      ["verify"]
    );

    // Convert hex signature to Uint8Array
    const sigBytes = new Uint8Array(
      signature.match(/.{1,2}/g)!.map(byte => parseInt(byte, 16))
    );

    return crypto.subtle.verify(
      "HMAC",
      key,
      sigBytes,
      encoder.encode(payload)
    );
  } catch (e) {
    console.error("Signature verification error:", e);
    return false;
  }
}

async function sendPurchase(env: Env, siteId: string, eventId: string, data: {
  orderId: string; value: number; currency: string; email?: string; fbp?: string; fbc?: string; eventSourceUrl?: string;
}) {
  const registry = await env.DB!.prepare(
    "SELECT dataset_id FROM meta_dataset_registry WHERE site_id = ? AND active = 1"
  ).bind(siteId).first<{ dataset_id: string }>();
  if (!registry) return;
  const existing = await env.DB!.prepare(
    "SELECT status FROM meta_event_ledger WHERE site_id = ? AND event_id = ? AND event_name = 'Purchase'"
  ).bind(siteId, eventId).first<{ status: string }>();
  if (existing?.status === "sent" || existing?.status === "pending") return;
  await env.DB!.prepare(
    `INSERT INTO meta_event_ledger (site_id, event_id, event_name, dataset_id, status, attempts)
     VALUES (?, ?, 'Purchase', ?, 'pending', 1)
     ON CONFLICT(site_id, event_id, event_name) DO UPDATE SET attempts = attempts + 1, status = 'pending'`
  ).bind(siteId, eventId, registry.dataset_id).run();
  const userData: Record<string, string> = {};
  if (data.email) userData.em = await sha256(data.email.trim().toLowerCase());
  const response = await fetch(
    `https://graph.facebook.com/${env.META_GRAPH_API_VERSION || "v20.0"}/${registry.dataset_id}/events?access_token=${encodeURIComponent(env.META_CAPI_ACCESS_TOKEN!)}`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        data: [{
          event_name: "Purchase",
          event_time: Math.floor(Date.now() / 1000),
          event_id: eventId,
          action_source: "website",
          event_source_url: data.eventSourceUrl,
          user_data: { ...userData, fbp: data.fbp, fbc: data.fbc },
          custom_data: { order_id: data.orderId, value: data.value, currency: data.currency.toUpperCase() },
        }],
      }),
    },
  );
  await env.DB!.prepare(
    "UPDATE meta_event_ledger SET status = ?, last_error = ?, updated_at = CURRENT_TIMESTAMP WHERE site_id = ? AND event_id = ? AND event_name = 'Purchase'"
  ).bind(response.ok ? "sent" : "dead_letter", response.ok ? null : (await response.text()).slice(0, 1000), siteId, eventId).run();
}

async function sha256(value: string) {
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(value));
  return [...new Uint8Array(digest)].map(byte => byte.toString(16).padStart(2, "0")).join("");
}
