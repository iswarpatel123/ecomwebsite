import "./hero.css";

/**
 * Static KATACHI hero (source port, no framer-motion).
 * Scroll/mount animations from the Next.js original are intentionally omitted.
 */
export default function HeroSection() {
  return (
    <section class="hero" aria-labelledby="hero-heading">
      <div class="hero__media" aria-hidden="true">
        <img
          class="hero__image"
          src="/assets/katachi/hero-background.jpeg"
          alt=""
          width={6144}
          height={6144}
          decoding="async"
          fetchpriority="high"
        />
        <div class="hero__overlay" />
      </div>

      <div class="hero__content">
        <div class="hero__container">
          <h1 id="hero-heading" class="hero__title">
            <span class="hero__title-line">Design furniture for</span>
            <span class="hero__title-line hero__title-line--italic">
              spaces that breathe.
            </span>
          </h1>
          <p class="hero__subtitle">
            Designed in Belgium, crafted to endure — timeless pieces for modern living.
          </p>
        </div>
      </div>

      <div class="hero__strip">
        <div class="hero__panel" role="region" aria-label="Shipping and guarantee highlights">
          <ul class="hero__highlights">
            <li class="hero__highlight">
              <svg
                class="hero__icon hero__icon--shipping"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                aria-hidden="true"
              >
                <path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z" />
                <path d="m3.3 7 8.7 5 8.7-5" />
                <path d="M12 22V12" />
                <path d="m9 11.5 6 3.5" />
              </svg>
              <span>Free shipping</span>
            </li>
            <li class="hero__highlight">
              <svg
                class="hero__icon hero__icon--delivery"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                aria-hidden="true"
              >
                <path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z" />
                <path d="m12 15-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z" />
                <path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0" />
                <path d="M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5" />
              </svg>
              <span>Delivered in 6 weeks</span>
            </li>
            <li class="hero__highlight">
              <svg
                class="hero__icon hero__icon--guarantee"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                aria-hidden="true"
              >
                <path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z" />
                <path d="m9 12 2 2 4-4" />
              </svg>
              <span>Lifetime guarantee</span>
            </li>
          </ul>
        </div>
      </div>
    </section>
  );
}
