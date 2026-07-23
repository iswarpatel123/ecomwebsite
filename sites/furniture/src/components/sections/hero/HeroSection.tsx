import { For, createSignal } from "solid-js";
import MediaGalleryGrid from "../media-gallery/MediaGallerySection.jsx";
import "./hero.css";

type ProductImage = { src: string; alt: string };
type Colour = { name: string; src: string };

const images: ProductImage[] = [
  { src: "/assets/koala/img-000-72dadcb6.png", alt: "Wanda Sofa Bed in olive green" },
  { src: "/assets/koala/img-001-8d40340b.png", alt: "Wanda Sofa Bed shown as a sofa" },
  { src: "/assets/koala/img-002-4cf4af0e.png", alt: "Wanda Sofa Bed shown as a bed" },
  { src: "/assets/koala/img-003-55b0da30.png", alt: "Wanda Sofa Bed detail" },
  { src: "/assets/koala/img-004-31bb2a9f.png", alt: "Wanda Sofa Bed in a living room" },
  { src: "/assets/koala/img-011-e891cc8a.png", alt: "Wanda Sofa Bed dimensions" },
];

const colours: Colour[] = [
  { name: "Australia 01 (Pantone)", src: "/assets/koala/img-038-0aefc6d3.png" },
  { name: "Morning Fog", src: "/assets/koala/img-042-2708913a.png" },
  { name: "Cinnamon Sky", src: "/assets/koala/img-043-69613acc.png" },
  { name: "Moonlit Silver", src: "/assets/koala/img-044-30301667.png" },
  { name: "Forest Dawn", src: "/assets/koala/img-045-37067ca1.png" },
  { name: "Silver Sand", src: "/assets/koala/img-046-a2cdf5a7.png" },
  { name: "Coastal Moss", src: "/assets/koala/img-047-b5b8d9d4.png" },
  { name: "Suffolk Sandstone", src: "/assets/koala/img-048-96d3c8a7.png" },
];

export function HeroSection() {
  const [selectedImage, setSelectedImage] = createSignal(0);
  const [size, setSize] = createSignal("99");
  const [colour, setColour] = createSignal(0);
  const [quantity, setQuantity] = createSignal(1);
  const [added, setAdded] = createSignal(false);

  const changeImage = (index: number) => setSelectedImage((index + images.length) % images.length);
  const adjustQuantity = (amount: number) => setQuantity((value) => Math.max(1, Math.min(10, value + amount)));
  const addToCart = () => {
    setAdded(true);
    window.setTimeout(() => setAdded(false), 2400);
  };

  return (
    <section class="hero" aria-labelledby="hero-product-title">
      <div class="hero__layout">
        {/* Left column: main image + desktop media grid (scrolls with page; summary sticks) */}
        <div class="hero__media" aria-label="Product photographs">
          <div class="hero__main-image-wrap">
            <img class="hero__main-image" src={images[selectedImage()].src} alt={images[selectedImage()].alt} />
            <button class="hero__gallery-nav hero__gallery-nav--previous" type="button" aria-label="Previous product photograph" onClick={() => changeImage(selectedImage() - 1)}>
              <span aria-hidden="true">‹</span>
            </button>
            <button class="hero__gallery-nav hero__gallery-nav--next" type="button" aria-label="Next product photograph" onClick={() => changeImage(selectedImage() + 1)}>
              <span aria-hidden="true">›</span>
            </button>
          </div>

          {/* Desktop only — replaces thumbnails */}
          <MediaGalleryGrid />

          {/* Mobile / tablet only — thumbnails replace the grid */}
          <div class="hero__thumbnails" role="list" aria-label="Choose product photograph">
            <For each={images}>
              {(image, index) => (
                <button
                  class="hero__thumbnail"
                  classList={{ "hero__thumbnail--selected": selectedImage() === index() }}
                  type="button"
                  role="listitem"
                  aria-label={`Show photograph ${index() + 1}`}
                  aria-current={selectedImage() === index() ? "true" : undefined}
                  onClick={() => setSelectedImage(index())}
                >
                  <img src={image.src} alt="" aria-hidden="true" />
                </button>
              )}
            </For>
          </div>
        </div>

        <div class="hero__summary">
          <a class="hero__back" href="#main-content">Sofa beds</a>
          <div class="hero__rating" aria-label="Rated 4.9 out of 5 stars from 222 reviews"><span aria-hidden="true">★★★★★</span> <u>4.9 (222 Reviews)</u></div>
          <h1 id="hero-product-title" class="hero__title">Wanda Sofa Bed</h1>
          <p class="hero__price">$3,295</p>
          <p class="hero__payments">or 4 interest-free payments of $823.75 with <strong>Afterpay</strong></p>
          <p class="hero__description">The comfiest, most versatile sofa bed around. Lounge, sleep, and make space for whatever life throws at you.</p>

          <fieldset class="hero__choice">
            <legend>Size <strong>{size()}"</strong></legend>
            <div class="hero__choices">
              <For each={["75", "99"]}>
                {(option) => <button type="button" class="hero__choice-button" classList={{ "is-selected": size() === option }} aria-pressed={size() === option} onClick={() => setSize(option)}>{option}"</button>}
              </For>
            </div>
          </fieldset>

          <fieldset class="hero__choice hero__choice--colour">
            <legend>Colour <strong>{colours[colour()].name}</strong></legend>
            <div class="hero__swatches">
              <For each={colours}>
                {(option, index) => <button type="button" class="hero__swatch" classList={{ "is-selected": colour() === index() }} aria-label={option.name} aria-pressed={colour() === index()} onClick={() => setColour(index())}><img src={option.src} alt="" aria-hidden="true" /></button>}
              </For>
            </div>
          </fieldset>

          <div class="hero__benefits" aria-label="Purchase benefits">
            <div><img src="/assets/koala/img-039-4432bd64.svg" alt="" aria-hidden="true" /><span>Free delivery</span></div>
            <div><img src="/assets/koala/img-040-cf67cad6.svg" alt="" aria-hidden="true" /><span>120-night trial</span></div>
            <div><img src="/assets/koala/img-041-563a3c24.svg" alt="" aria-hidden="true" /><span>10-year warranty</span></div>
          </div>

          <div class="hero__purchase">
            <div class="hero__quantity" aria-label="Quantity">
              <button type="button" aria-label="Decrease quantity" onClick={() => adjustQuantity(-1)} disabled={quantity() === 1}>−</button>
              <output aria-live="polite">{quantity()}</output>
              <button type="button" aria-label="Increase quantity" onClick={() => adjustQuantity(1)} disabled={quantity() === 10}>+</button>
            </div>
            <button class="hero__add" type="button" onClick={addToCart}>{added() ? "Added to cart" : `Add to cart • $${(3295 * quantity()).toLocaleString()}`}</button>
          </div>
          <p class="hero__notice" aria-live="polite">{added() ? "Wanda Sofa Bed has been added to your cart." : ""}</p>
        </div>
      </div>
    </section>
  );
}

export default HeroSection;
