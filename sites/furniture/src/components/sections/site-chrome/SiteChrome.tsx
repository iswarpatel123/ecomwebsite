import { useLocation } from "@solidjs/router";
import {
  NewsletterCta,
  SiteFooter,
  SiteHeader,
  TopBanner,
  type NavDropdownItem,
  type SiteHeaderNavItem,
} from "@repo/storefront-patterns";
import "./site-chrome.css";

const COLLECTION = "/collections";

const MODULAR_SUBCATEGORIES: NavDropdownItem[] = [
  {
    id: "2-seater",
    label: "2-Seater Sofas",
    href: COLLECTION,
    imageSrc: "/assets/koala/img-008-9b032ead.png",
    imageAlt: "2-Seater sofa",
  },
  {
    id: "3-seater",
    label: "3-Seater Sofas",
    href: COLLECTION,
    imageSrc: "/assets/koala/img-001-8d40340b.png",
    imageAlt: "3-Seater sofa",
  },
  {
    id: "large",
    label: "Large Sofas",
    href: COLLECTION,
    imageSrc: "/assets/koala/img-004-31bb2a9f.png",
    imageAlt: "Large sofa",
  },
  {
    id: "chaise",
    label: "Chaise Sofas",
    href: COLLECTION,
    imageSrc: "/assets/koala/img-015-179c25f4.png",
    imageAlt: "Chaise sofa",
  },
  {
    id: "corner",
    label: "Corner Sofas",
    href: COLLECTION,
    imageSrc: "/assets/koala/img-003-55b0da30.png",
    imageAlt: "Corner sofa",
  },
  {
    id: "armchairs",
    label: "Armchairs",
    href: COLLECTION,
    imageSrc: "/assets/koala/img-006-553b3ba8.png",
    imageAlt: "Armchair",
  },
  {
    id: "ottomans",
    label: "Ottomans",
    href: COLLECTION,
    imageSrc: "/assets/koala/img-007-c460d576.png",
    imageAlt: "Ottoman",
  },
];

const NAV_ITEMS: SiteHeaderNavItem[] = [
  { label: "Best Sellers", href: COLLECTION },
  { label: "Sofa Beds", href: COLLECTION },
  {
    label: "Modular Sofas",
    href: COLLECTION,
    children: MODULAR_SUBCATEGORIES,
    dropdownVariant: "cards",
  },
  { label: "Accessories", href: COLLECTION },
  { label: "Mattresses", href: COLLECTION },
];

/** Shared top banner + primary nav for PDP and collection pages. */
export function StorefrontChrome() {
  const location = useLocation();

  return (
    <>
      <TopBanner
        messages={[
          "Free Shipping & 120 Day Free Returns",
          "120 Day Free Returns on every order",
          "Fast delivery to most metro areas",
          "5-Year Warranty on sofas & sofa beds",
        ]}
        intervalMs={4000}
        links={[
          { label: "Help Centre", href: "#faq" },
          { label: "Contact", href: "#" },
        ]}
      />
      <SiteHeader
        brand="koala"
        brandHref="/"
        activeLabel={location.pathname.startsWith("/collections") ? "Modular Sofas" : undefined}
        navItems={NAV_ITEMS}
      />
    </>
  );
}

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
              { label: "Koala Sofa Bed [4th Gen]", href: "/" },
              { label: "Byron Sofa Bed [3rd Gen]", href: "/" },
              { label: "Torquay Modular Sofa", href: "/" },
              { label: "Bangalow Modular Sofa", href: "/" },
              { label: "Wanda Sofa Bed", href: "/" },
              { label: "Tamarama Modular Sofa", href: "/" },
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
