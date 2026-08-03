import { Title } from "@solidjs/meta";
import { onMount } from "solid-js";
import { AnalyticsManager, MetaPixelProvider } from "@dropshipping/analytics";

export default function Home() {
  onMount(() => {
    const analytics = new AnalyticsManager();
    analytics.registerProvider(new MetaPixelProvider({
      enabled: false,
      send_browser_events: true,
      consent_required: false,
    }));
    analytics.trackEvent("page_view");
  });

  return (
    <>
      <Title>Welcome</Title>
      <main class="min-h-screen flex items-center justify-center">
        <h1 class="text-4xl font-bold">Welcome to @dropshipping/site</h1>
      </main>
    </>
  );
}