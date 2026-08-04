import { NewsletterCta, SiteFooter } from "@repo/storefront-patterns";
import "./site-chrome.css";

export function NewsletterSection() {
  return (
    <div class="site-chrome__newsletter">
      <NewsletterCta title="Sign up and save on your first order" buttonLabel="Sign up now" href="#" />
    </div>
  );
}

export function FooterSection() {
  return (
    <div class="site-chrome__footer">
      <SiteFooter
        brand="koala"
        acknowledgement={
          "In the spirit of reconciliation, Koala acknowledges the Traditional Custodians of Country throughout Australia and their connections to land, sea and community.\n\nWe pay our respect to their Elders past and present and extend that respect to all Aboriginal and Torres Strait Islander peoples today."
        }
        socialLinks={[
          { label: "Facebook", href: "#" },
          { label: "Instagram", href: "#" },
        ]}
        columns={[
          {
            title: "Products",
            links: [
              { label: "Koala Sofa Bed [4th Gen]", href: "#" },
              { label: "Byron Sofa Bed [3rd Gen]", href: "#" },
              { label: "Torquay Modular Sofa", href: "#" },
              { label: "Bangalow Modular Sofa", href: "#" },
              { label: "Wanda Sofa Bed", href: "#" },
              { label: "Tamarama Modular Sofa", href: "#" },
            ],
          },
          {
            title: "Discover",
            links: [
              { label: "Our Story", href: "#" },
              { label: "Innovation", href: "#" },
              { label: "Careers", href: "#" },
              { label: "Financing", href: "#" },
              { label: "Reviews", href: "#reviews" },
              { label: "Treetops Blog", href: "#" },
            ],
          },
          {
            title: "Questions",
            links: [
              { label: "Returns & Warranty", href: "#" },
              { label: "Delivery & Shipping", href: "#" },
              { label: "120 Day Free Returns", href: "#" },
              { label: "Help Center", href: "#faq" },
              { label: "Contact Us", href: "#" },
              { label: "Referral Terms", href: "#" },
            ],
          },
        ]}
        copyright="© 2026 Koala"
        legalLinks={[
          { label: "Terms of Use", href: "#" },
          { label: "Privacy Policy", href: "#" },
          { label: "Legal", href: "#" },
          { label: "Accessibility", href: "#" },
          { label: "Cookie Preferences", href: "#" },
          { label: "Do Not Sell or Share", href: "#" },
        ]}
        paymentLabels={["Amex", "Apple Pay", "Mastercard", "PayPal", "Shop Pay", "Visa", "Afterpay"]}
      />
    </div>
  );
}
