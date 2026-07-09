import { Cart } from "@dropshipping/core-commerce";

export interface PaymentProcessor {
  name: string;
  createPaymentIntent(cart: Cart, currency: string): Promise<{ clientSecret: string; transactionId: string }>;
  confirmPayment(transactionId: string): Promise<{ success: boolean; error?: string }>;
}

export class StripePaymentProcessor implements PaymentProcessor {
  name = "Stripe";
  private apiKey: string;

  constructor(apiKey: string) {
    this.apiKey = apiKey;
  }

  async createPaymentIntent(cart: Cart, currency = "usd") {
    const amountInCents = Math.round(cart.total * 100);
    return {
      clientSecret: `pi_mock_${Math.random().toString(36).substring(7)}_secret_${Math.random().toString(36).substring(7)}`,
      transactionId: `ch_mock_${Math.random().toString(36).substring(7)}`,
      amount: amountInCents,
      currency
    };
  }

  async confirmPayment(transactionId: string) {
    return {
      success: true,
      transactionId
    };
  }
}

export class BraintreePaymentProcessor implements PaymentProcessor {
  name = "Braintree";
  private tokenizationKey: string;

  constructor(tokenizationKey: string) {
    this.tokenizationKey = tokenizationKey;
  }

  async createPaymentIntent(cart: Cart, currency = "usd") {
    return {
      clientSecret: `braintree_client_token_mock_${Math.random().toString(36).substring(7)}`,
      transactionId: `bt_tx_mock_${Math.random().toString(36).substring(7)}`
    };
  }

  async confirmPayment(transactionId: string) {
    return {
      success: true,
      transactionId
    };
  }
}
