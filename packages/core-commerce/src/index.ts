export interface Product {
  id: string;
  name: string;
  price: number;
  sku: string;
  niche: string;
  description?: string;
  image?: string;
  metadata?: Record<string, any>;
}

export interface CartItem {
  product: Product;
  quantity: number;
}

export interface Cart {
  items: CartItem[];
  subtotal: number;
  tax: number;
  shipping: number;
  total: number;
}

export interface CustomerDetails {
  email: string;
  firstName: string;
  lastName: string;
  shippingAddress: {
    line1: string;
    line2?: string;
    city: string;
    state: string;
    postalCode: string;
    country: string;
  };
}

export interface Order {
  id: string;
  tenantId: string;
  siteId: string;
  items: CartItem[];
  subtotal: number;
  tax: number;
  shipping: number;
  total: number;
  customer: CustomerDetails;
  status: 'pending' | 'paid' | 'shipped' | 'cancelled';
  createdAt: string;
}

// Commerce Calculators
export function calculateCart(items: CartItem[], shippingRate = 0, taxRate = 0.08): Cart {
  const subtotal = items.reduce((sum, item) => sum + item.product.price * item.quantity, 0);
  const tax = subtotal * taxRate;
  const total = subtotal + tax + shippingRate;

  return {
    items,
    subtotal: Math.round(subtotal * 100) / 100,
    tax: Math.round(tax * 100) / 100,
    shipping: Math.round(shippingRate * 100) / 100,
    total: Math.round(total * 100) / 100,
  };
}

export function createCartState() {
  let items: CartItem[] = [];

  return {
    getItems: () => items,
    addItem: (product: Product, quantity = 1) => {
      const existing = items.find(i => i.product.id === product.id);
      if (existing) {
        existing.quantity += quantity;
      } else {
        items.push({ product, quantity });
      }
    },
    removeItem: (productId: string) => {
      items = items.filter(i => i.product.id !== productId);
    },
    updateQuantity: (productId: string, quantity: number) => {
      const existing = items.find(i => i.product.id === productId);
      if (existing) {
        existing.quantity = Math.max(1, quantity);
      }
    },
    clear: () => {
      items = [];
    }
  };
}
