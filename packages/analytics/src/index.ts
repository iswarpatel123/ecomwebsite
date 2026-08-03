export type AnalyticsEventName =
  | "page_view"
  | "view_item"
  | "add_to_cart"
  | "remove_from_cart"
  | "begin_checkout"
  | "purchase";

export interface AnalyticsEvent {
  name: AnalyticsEventName;
  properties?: Record<string, any>;
  timestamp: number;
  eventId?: string;
}

export interface AnalyticsProvider {
  track(event: AnalyticsEvent): void;
}

export interface MetaPixelConfig {
  enabled: boolean;
  pixel_id?: string;
  send_browser_events?: boolean;
  consent_required?: boolean;
}

export type AdvertisingConsent = boolean | (() => boolean);

export interface CheckoutAttribution {
  eventId: string;
  fbp?: string;
  fbc?: string;
  eventSourceUrl?: string;
}

export function createEventId(prefix = "evt") {
  const id = typeof crypto !== "undefined" && crypto.randomUUID
    ? crypto.randomUUID()
    : `${Date.now()}-${Math.random().toString(36).slice(2)}`;
  return `${prefix}_${id}`;
}

export function getCheckoutAttribution(eventId = createEventId("checkout")): CheckoutAttribution {
  if (typeof window === "undefined") return { eventId };
  const cookies = document.cookie.split(";").map(cookie => cookie.trim());
  const read = (name: string) => cookies.find(cookie => cookie.startsWith(`${name}=`))?.slice(name.length + 1);
  const url = new URL(window.location.href);
  const fbp = read("_fbp");
  const fbc = read("_fbc") || (url.searchParams.get("fbclid") ? `fb.1.${Date.now()}.${url.searchParams.get("fbclid")}` : undefined);
  return { eventId, fbp, fbc, eventSourceUrl: window.location.href };
}

export interface CheckoutSessionPayload {
  siteId: string;
  lineItems: unknown[];
  successUrl: string;
  cancelUrl: string;
  attribution: CheckoutAttribution;
}

export async function createCheckoutSession(endpoint: string, payload: CheckoutSessionPayload) {
  const response = await fetch(`${endpoint.replace(/\/$/, "")}/checkout/session`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      ...payload,
      checkoutEventId: payload.attribution.eventId,
      fbp: payload.attribution.fbp,
      fbc: payload.attribution.fbc,
      eventSourceUrl: payload.attribution.eventSourceUrl,
    }),
  });
  if (!response.ok) throw new Error(`Checkout session failed (${response.status})`);
  return response.json();
}

const META_EVENT_NAMES: Partial<Record<AnalyticsEventName, string>> = {
  page_view: "PageView",
  view_item: "ViewContent",
  add_to_cart: "AddToCart",
  begin_checkout: "InitiateCheckout",
  purchase: "Purchase",
};

declare global {
  interface Window {
    fbq?: (...args: any[]) => void;
    __metaPixelInitialized?: Set<string>;
  }
}

export class MetaPixelProvider implements AnalyticsProvider {
  private readonly config: MetaPixelConfig;
  private readonly consent: AdvertisingConsent;

  constructor(config: MetaPixelConfig, consent: AdvertisingConsent = true) {
    this.config = config;
    this.consent = consent;
  }

  track(event: AnalyticsEvent) {
    if (
      typeof window === "undefined" ||
      !this.config.enabled ||
      this.config.send_browser_events === false ||
      !this.config.pixel_id ||
      !this.hasConsent()
    ) return;

    const eventName = META_EVENT_NAMES[event.name];
    if (!eventName || typeof window.fbq !== "function") return;
    if (!window.__metaPixelInitialized) window.__metaPixelInitialized = new Set();
    if (!window.__metaPixelInitialized.has(this.config.pixel_id)) {
      window.fbq("init", this.config.pixel_id);
      window.__metaPixelInitialized.add(this.config.pixel_id);
    }

    const properties = { ...(event.properties || {}) };
    if (event.eventId) properties.eventID = event.eventId;
    window.fbq("track", eventName, properties);
  }

  private hasConsent() {
    return typeof this.consent === "function" ? this.consent() : this.consent;
  }
}

export class GoogleAnalyticsProvider implements AnalyticsProvider {
  private measurementId: string;

  constructor(measurementId: string) {
    this.measurementId = measurementId;
  }

  track(event: AnalyticsEvent) {
    if (typeof window !== "undefined" && (window as any).gtag) {
      (window as any).gtag("event", event.name, {
        send_to: this.measurementId,
        ...event.properties,
      });
    } else {
      console.log(
        `[GA-SSR/Mock] Track Event - ID: ${this.measurementId}, Name: ${event.name}`,
        event.properties
      );
    }
  }
}

export class CustomTrackingProvider implements AnalyticsProvider {
  private endpoint: string;
  private tenantId: string;

  constructor(endpoint: string, tenantId: string) {
    this.endpoint = endpoint;
    this.tenantId = tenantId;
  }

  track(event: AnalyticsEvent) {
    const payload = {
      ...event,
      tenantId: this.tenantId,
    };
    console.log(`[CustomTracking] Posting to ${this.endpoint}:`, payload);
  }
}

export class AnalyticsManager {
  private providers: AnalyticsProvider[] = [];

  registerProvider(provider: AnalyticsProvider) {
    this.providers.push(provider);
  }

  trackEvent(name: AnalyticsEventName, properties?: Record<string, any>, eventId?: string) {
    const event: AnalyticsEvent = {
      name,
      properties,
      timestamp: Date.now(),
      eventId: eventId || (typeof crypto !== "undefined" && crypto.randomUUID ? crypto.randomUUID() : `${Date.now()}-${Math.random()}`),
    };

    for (const provider of this.providers) {
      try {
        provider.track(event);
      } catch (err) {
        console.error("Failed to track event on provider", err);
      }
    }
  }
}
