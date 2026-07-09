import { Title } from "@solidjs/meta";
import { For, createSignal, onMount } from "solid-js";
import { Button, PriceFormatter } from "@dropshipping/ui-primitives";
import { calculateCart, Product, CartItem } from "@dropshipping/core-commerce";
import { validateSiteConfig, SiteConfig } from "@dropshipping/config-validation";
import { AnalyticsManager, GoogleAnalyticsProvider } from "@dropshipping/analytics";
import { StripePaymentProcessor } from "@dropshipping/stripe-client";

// Mock Tenant Config retrieved from Cloudflare KV/D1
const mockTenantConfig: SiteConfig = validateSiteConfig({
  siteId: "site_furn_01",
  tenantId: "tenant_cozy_living",
  domain: "cozy-furniture.example.com",
  siteName: "Cozy Furniture Niche Hub",
  niche: "furniture",
  theme: {
    primaryColor: "#4f46e5",
    secondaryColor: "#111827",
    fontFamily: "sans-serif",
  },
  integrations: {
    stripePublishableKey: "pk_test_furniture_key_123",
    googleAnalyticsId: "UA-FURN-MOCK",
  },
  features: {
    enableReviews: true,
    enableInstalls: true,
    enableCustomQuote: false,
  },
});

const FURNITURE_PRODUCTS: Product[] = [
  { id: "p1", name: "Modern Oak Dining Table", price: 799.0, sku: "FURN-OAK-TAB", niche: "furniture" },
  { id: "p2", name: "Ergonomic Office Chair", price: 249.5, sku: "FURN-ERG-CHR", niche: "furniture" },
  { id: "p3", name: "Velvet Chesterfield Sofa", price: 1299.0, sku: "FURN-VLV-SOF", niche: "furniture" },
];

export default function Home() {
  const [cartItems, setCartItems] = createSignal<CartItem[]>([]);
  const analytics = new AnalyticsManager();

  onMount(() => {
    analytics.registerProvider(new GoogleAnalyticsProvider(mockTenantConfig.integrations.googleAnalyticsId || ""));
    analytics.trackEvent("page_view", { siteId: mockTenantConfig.siteId });
  });

  const cartCalculations = () => calculateCart(cartItems(), 50, 0.08); // $50 flat shipping for heavy furniture

  const addToCart = (product: Product) => {
    const existing = cartItems().find(item => item.product.id === product.id);
    if (existing) {
      setCartItems(
        cartItems().map(item =>
          item.product.id === product.id ? { ...item, quantity: item.quantity + 1 } : item
        )
      );
    } else {
      setCartItems([...cartItems(), { product, quantity: 1 }]);
    }
    analytics.trackEvent("add_to_cart", { productSku: product.sku, price: product.price });
  };

  const checkout = async () => {
    analytics.trackEvent("begin_checkout", { total: cartCalculations().total });
    const stripe = new StripePaymentProcessor(mockTenantConfig.integrations.stripePublishableKey);
    const result = await stripe.createPaymentIntent(cartCalculations());

    alert(`Checkout initiated! Payment intent created via Stripe: ${result.clientSecret}\nMock Transaction ID: ${result.transactionId}`);

    analytics.trackEvent("purchase", { total: cartCalculations().total, transactionId: result.transactionId });
    setCartItems([]);
  };

  return (
    <main class="p-6 font-sans">
      <Title>{mockTenantConfig.siteName}</Title>

      <header class="mb-8 border-b pb-4">
        <h1 class="text-3xl font-extrabold text-gray-900">{mockTenantConfig.siteName}</h1>
        <p class="text-sm text-gray-500">Premium dropshipped furniture delivered to your door.</p>
      </header>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Products Grid */}
        <div>
          <h2 class="text-xl font-bold mb-4">Our Curated Catalog</h2>
          <div class="space-y-4">
            <For each={FURNITURE_PRODUCTS}>
              {(product) => (
                <div class="border p-4 rounded-lg flex justify-between items-center bg-white shadow-sm">
                  <div>
                    <h3 class="font-semibold text-lg">{product.name}</h3>
                    <p class="text-xs text-gray-400">SKU: {product.sku}</p>
                    <div class="mt-1">
                      <PriceFormatter amount={product.price} />
                    </div>
                  </div>
                  <Button variant="primary" onClick={() => addToCart(product)}>
                    Add to Cart
                  </Button>
                </div>
              )}
            </For>
          </div>
        </div>

        {/* Shopping Cart & Checkout */}
        <div class="border p-6 rounded-lg bg-gray-50 h-fit">
          <h2 class="text-xl font-bold mb-4">Shopping Cart</h2>

          <For each={cartItems()} fallback={<p class="text-gray-400">Your cart is empty.</p>}>
            {(item) => (
              <div class="flex justify-between items-center mb-3">
                <div>
                  <span class="font-medium">{item.product.name}</span>
                  <span class="text-gray-500 text-sm block">Qty: {item.quantity}</span>
                </div>
                <PriceFormatter amount={item.product.price * item.quantity} />
              </div>
            )}
          </For>

          <div class="border-t mt-4 pt-4 space-y-2">
            <div class="flex justify-between text-sm text-gray-600">
              <span>Subtotal:</span>
              <PriceFormatter amount={cartCalculations().subtotal} />
            </div>
            <div class="flex justify-between text-sm text-gray-600">
              <span>Tax (8%):</span>
              <PriceFormatter amount={cartCalculations().tax} />
            </div>
            <div class="flex justify-between text-sm text-gray-600">
              <span>Shipping:</span>
              <PriceFormatter amount={cartCalculations().shipping} />
            </div>
            <div class="flex justify-between font-bold text-lg text-gray-900 border-t pt-2 mt-2">
              <span>Total:</span>
              <PriceFormatter amount={cartCalculations().total} />
            </div>
          </div>

          <Button
            variant="secondary"
            class="w-full mt-6"
            disabled={cartItems().length === 0}
            onClick={checkout}
          >
            Pay with Stripe
          </Button>
        </div>
      </div>
    </main>
  );
}
