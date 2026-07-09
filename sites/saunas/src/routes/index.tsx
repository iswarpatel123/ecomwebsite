import { Title } from "@solidjs/meta";
import { For, createSignal, onMount } from "solid-js";
import { Button, PriceFormatter } from "@dropshipping/ui-primitives";
import { calculateCart, Product, CartItem } from "@dropshipping/core-commerce";
import { validateSiteConfig, SiteConfig } from "@dropshipping/config-validation";
import { AnalyticsManager, CustomTrackingProvider } from "@dropshipping/analytics";
import { BraintreePaymentProcessor } from "@dropshipping/stripe-client";

// High-ticket sauna tenant config
const mockTenantConfig: SiteConfig = validateSiteConfig({
  siteId: "site_sauna_99",
  tenantId: "tenant_nordic_glow",
  domain: "nordic-glow-saunas.example.com",
  siteName: "Nordic Glow Luxury Saunas",
  niche: "saunas",
  theme: {
    primaryColor: "#78350f", // Amber/warm wood
    secondaryColor: "#451a03",
    fontFamily: "serif",
  },
  integrations: {
    stripePublishableKey: "pk_test_saunas_braintree_fallback",
    braintreeTokenizationKey: "bt_tok_nordic_saunas_99",
  },
  features: {
    enableReviews: true,
    enableInstalls: true,
    enableCustomQuote: true, // Saunas are highly customized, high-ticket items
  },
});

const SAUNA_PRODUCTS: Product[] = [
  { id: "s1", name: "Nordic Outdoor Barrel Sauna (4-Person)", price: 5499.0, sku: "SAUN-BAR-4P", niche: "saunas" },
  { id: "s2", name: "Indoor Far-Infrared Cabin", price: 3899.0, sku: "SAUN-INF-CAB", niche: "saunas" },
  { id: "s3", name: "Traditional Finnish Sauna Heater (9kW)", price: 899.0, sku: "SAUN-HTR-9KW", niche: "saunas" },
];

export default function Home() {
  const [cartItems, setCartItems] = createSignal<CartItem[]>([]);
  const [selectedWood, setSelectedWood] = createSignal<"cedar" | "hemlock">("cedar");
  const [installService, setInstallService] = createSignal<boolean>(false);
  const analytics = new AnalyticsManager();

  onMount(() => {
    analytics.registerProvider(new CustomTrackingProvider("/api/logs", mockTenantConfig.tenantId));
    analytics.trackEvent("page_view", { siteId: mockTenantConfig.siteId });
  });

  const cartCalculations = () => {
    const additionalFees = installService() ? 499 : 0;
    return calculateCart(cartItems(), 250 + additionalFees, 0.05); // High-ticket saunas $250 base freight shipping
  };

  const addToCart = (product: Product) => {
    const customizedProduct = {
      ...product,
      name: `${product.name} (${selectedWood() === "cedar" ? "Western Red Cedar" : "Canadian Hemlock"})`,
      price: selectedWood() === "cedar" ? product.price + 300 : product.price, // Cedar upcharge
    };

    const existing = cartItems().find(item => item.product.id === product.id);
    if (existing) {
      setCartItems(
        cartItems().map(item =>
          item.product.id === product.id ? { ...item, quantity: item.quantity + 1 } : item
        )
      );
    } else {
      setCartItems([...cartItems(), { product: customizedProduct, quantity: 1 }]);
    }
    analytics.trackEvent("add_to_cart", { productSku: product.sku, wood: selectedWood(), installService: installService() });
  };

  const checkout = async () => {
    analytics.trackEvent("begin_checkout", { total: cartCalculations().total });

    const braintree = new BraintreePaymentProcessor(mockTenantConfig.integrations.braintreeTokenizationKey || "default_tok");
    const result = await braintree.createPaymentIntent(cartCalculations());

    alert(`Checkout initiated! Payment intent created via Braintree: ${result.clientSecret}\nMock Braintree Transaction ID: ${result.transactionId}`);

    analytics.trackEvent("purchase", { total: cartCalculations().total, transactionId: result.transactionId });
    setCartItems([]);
  };

  const requestCustomQuote = () => {
    alert("Our custom backyard designers will contact you within 24 hours with a comprehensive design layout blueprint and custom quote!");
    analytics.trackEvent("page_view", { form: "custom_quote_sauna" });
  };

  return (
    <main class="p-6 md:p-12 max-w-7xl mx-auto font-serif">
      <Title>{mockTenantConfig.siteName}</Title>

      <header class="mb-12 border-b border-amber-900/10 pb-6 text-center">
        <h1 class="text-4xl font-extrabold text-amber-950">{mockTenantConfig.siteName}</h1>
        <p class="text-md text-amber-850 italic mt-2">Authentic wellness & high-ticket home saunas designed for generations.</p>
      </header>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-12">
        {/* Niche Specific Interactions / Sauna Builder Customizations */}
        <div class="lg:col-span-2 space-y-8">
          <div class="bg-amber-50 p-6 rounded-xl border border-amber-900/10 shadow-sm">
            <h2 class="text-2xl font-semibold text-amber-950 mb-4">Step 1: Choose Your Sauna Wood Spec</h2>
            <div class="grid grid-cols-2 gap-4">
              <label
                class={`p-4 border rounded-lg cursor-pointer block text-center transition-all ${
                  selectedWood() === "cedar" ? "bg-amber-900 text-white border-amber-900 shadow" : "bg-white text-gray-700 border-gray-200"
                }`}
              >
                <input
                  type="radio"
                  name="wood"
                  value="cedar"
                  class="sr-only"
                  checked={selectedWood() === "cedar"}
                  onChange={() => setSelectedWood("cedar")}
                />
                <span class="font-bold block text-lg">Western Red Cedar</span>
                <span class="text-sm opacity-90">+$300.00 (Highly aromatic)</span>
              </label>

              <label
                class={`p-4 border rounded-lg cursor-pointer block text-center transition-all ${
                  selectedWood() === "hemlock" ? "bg-amber-900 text-white border-amber-900 shadow" : "bg-white text-gray-700 border-gray-200"
                }`}
              >
                <input
                  type="radio"
                  name="wood"
                  value="hemlock"
                  class="sr-only"
                  checked={selectedWood() === "hemlock"}
                  onChange={() => setSelectedWood("hemlock")}
                />
                <span class="font-bold block text-lg">Canadian Hemlock</span>
                <span class="text-sm opacity-90">Included (Classic, durable)</span>
              </label>
            </div>

            <div class="mt-6 flex items-center bg-white p-4 rounded-lg border border-gray-200">
              <input
                id="install"
                type="checkbox"
                checked={installService()}
                onChange={(e) => setInstallService(e.currentTarget.checked)}
                class="w-5 h-5 accent-amber-900 mr-3"
              />
              <label for="install" class="text-sm text-gray-700 cursor-pointer">
                <strong>Add Professional Backyard White-Glove Installation</strong> (+$499.00)
              </label>
            </div>
          </div>

          <h2 class="text-2xl font-semibold text-amber-950">Select Your Luxury Sauna Configuration</h2>
          <div class="space-y-4">
            <For each={SAUNA_PRODUCTS}>
              {(product) => (
                <div class="border border-gray-200 p-6 rounded-xl flex flex-col md:flex-row justify-between items-start md:items-center bg-white shadow-sm gap-4">
                  <div>
                    <h3 class="font-bold text-xl text-amber-950">{product.name}</h3>
                    <p class="text-sm text-gray-500">Premium commercial-grade hardware. SKU: {product.sku}</p>
                    <div class="mt-2 text-lg">
                      <PriceFormatter amount={product.price} />
                    </div>
                  </div>
                  <div class="flex gap-2">
                    <Button variant="primary" onClick={() => addToCart(product)} class="!bg-amber-950 hover:!bg-amber-900">
                      Build & Cart
                    </Button>
                    {mockTenantConfig.features.enableCustomQuote && product.price > 1000 && (
                      <Button variant="outline" onClick={requestCustomQuote}>
                        Custom Quote
                      </Button>
                    )}
                  </div>
                </div>
              )}
            </For>
          </div>
        </div>

        {/* High Ticket Order Summary / Cart */}
        <div class="border border-amber-900/10 p-6 rounded-xl bg-amber-50/50 shadow-sm h-fit">
          <h2 class="text-2xl font-bold text-amber-950 mb-4">Sauna Configuration</h2>

          <For each={cartItems()} fallback={<p class="text-gray-400 italic">No saunas or heaters configured in your checkout yet.</p>}>
            {(item) => (
              <div class="flex justify-between items-start mb-4 border-b border-amber-900/10 pb-3">
                <div>
                  <span class="font-semibold text-amber-950 text-md block">{item.product.name}</span>
                  <span class="text-gray-500 text-sm">Qty: {item.quantity}</span>
                </div>
                <PriceFormatter amount={item.product.price * item.quantity} />
              </div>
            )}
          </For>

          <div class="space-y-3 mt-4 pt-2">
            <div class="flex justify-between text-sm text-amber-900/80">
              <span>Subtotal:</span>
              <PriceFormatter amount={cartCalculations().subtotal} />
            </div>
            {installService() && (
              <div class="flex justify-between text-sm text-green-700 font-medium">
                <span>Installation Service:</span>
                <span>$499.00</span>
              </div>
            )}
            <div class="flex justify-between text-sm text-amber-900/80">
              <span>Freight Shipping & Handling:</span>
              <PriceFormatter amount={250} />
            </div>
            <div class="flex justify-between text-sm text-amber-900/80">
              <span>Tax (5% state exemptions):</span>
              <PriceFormatter amount={cartCalculations().tax} />
            </div>
            <div class="flex justify-between font-extrabold text-xl text-amber-950 border-t border-amber-900/20 pt-3 mt-3">
              <span>Order Total:</span>
              <PriceFormatter amount={cartCalculations().total} />
            </div>
          </div>

          <Button
            variant="secondary"
            class="w-full mt-6 !bg-amber-950 hover:!bg-amber-900"
            disabled={cartItems().length === 0}
            onClick={checkout}
          >
            Authorize Braintree Payment
          </Button>

          <p class="text-xs text-center text-gray-400 mt-4">
            Secured and encrypted by Braintree & Cloudflare. Escrow compliance active for heavy freight.
          </p>
        </div>
      </div>
    </main>
  );
}
