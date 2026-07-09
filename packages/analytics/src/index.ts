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
}

export interface AnalyticsProvider {
  track(event: AnalyticsEvent): void;
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

  trackEvent(name: AnalyticsEventName, properties?: Record<string, any>) {
    const event: AnalyticsEvent = {
      name,
      properties,
      timestamp: Date.now(),
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
