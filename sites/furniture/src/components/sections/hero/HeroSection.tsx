import { For, createSignal } from "solid-js";
import { ProductDescription, type AccordionSection } from "@repo/storefront-patterns";
import MediaGalleryGrid from "../media-gallery/MediaGallerySection.jsx";
import "./hero.css";

type ProductImage = { src: string; alt: string };
type Colour = { name: string; src: string };

const images: ProductImage[] = [
  { src: "/assets/koala/img-000-dark-grey.png", alt: "Wanda Sofa Bed in dark grey" },
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

const detailSections: AccordionSection[] = [
  {
    id: "description",
    title: "Product Description",
    content: "The comfiest, most versatile sofa bed around. Lounge, sleep, and make space for whatever life throws at you. Our signature CloudCell™ comfort technology, perfected over years, built into a sofa.",
  },
  {
    id: "assembly",
    title: "Assembly Instructions",
    content: "Your Wanda Sofa Bed arrives ready to assemble in minutes. No tools, no handyman, no YouTube tutorials. Clear instructions, click-together components, and everything you need is in the box.",
  },
  {
    id: "features",
    title: "Key Features",
    content: "<ul><li>Flip-from-sofa-to-bed design</li><li>Signature CloudCell™ comfort</li><li>Removable, machine-washable covers</li><li>Water and stain-resistant fabric</li><li>No tools required for assembly</li></ul>",
  },
  {
    id: "dimensions",
    title: "Dimensions",
    content: "<p><strong>Sofa mode:</strong> W 99cm × D 85cm × H 82cm</p><p><strong>Bed mode:</strong> W 99cm × D 160cm × H 45cm</p><p><strong>Seat height:</strong> 45cm</p><p><strong>Weight:</strong> 42kg</p>",
  },
  {
    id: "materials",
    title: "Materials",
    content: "<p><strong>Frame:</strong> Kiln-dried hardwood, steel reinforcements</p><p><strong>Cushion fill:</strong> CloudCell™ foam + fibre top</p><p><strong>Upholstery:</strong> 100% polyester, water-resistant finish</p><p><strong>Legs:</strong> Solid timber, black finish</p>",
  },
  {
    id: "care",
    title: "Care",
    content: "<p>Remove covers by unzipping. Machine wash cold on gentle cycle. Tumble dry low or line dry. Re-zip and restore. Spot clean frame with damp cloth.</p>",
  },
  {
    id: "returns",
    title: "120-Day Free Returns",
    content: "<p>Buy with complete confidence. Every Wanda Sofa Bed comes with 120-day free returns. That's four months to live on it, sleep on it, and love it. If it's not right, we'll collect it for free.</p>",
  },
  {
    id: "delivery",
    title: "Delivery & Package Size",
    content: "<p><strong>Free delivery</strong> to most metro areas. Ships in 2 boxes:</p><ul><li>Box 1: 105cm × 55cm × 45cm (28kg)</li><li>Box 2: 105cm × 55cm × 45cm (14kg)</li></ul><p>Express delivery available at checkout.</p>",
  },
];

export function HeroSection() {
  const [selectedImage, setSelectedImage] = createSignal(0);
  const [size, setSize] = createSignal("99");
  const [colour, setColour] = createSignal(0);

  const changeImage = (index: number) => setSelectedImage((index + images.length) % images.length);

  return (
    <section class="hero" aria-labelledby="hero-product-title">
      <div class="hero__layout">
        {/* Left column: main image + desktop media grid */}
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

          <MediaGalleryGrid />

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

        {/* Right column: product description panel */}
        <div class="hero__summary">
          <ProductDescription
            title="Wanda Sofa Bed"
            price="$3,295"
            breadcrumbLabel="Sofa beds"
            breadcrumbHref="#"
            rating={4.9}
            reviewCount={222}
            paymentPlan="or 4 interest-free payments of $823.75 with Afterpay"
            benefits={[
              { icon: "/assets/koala/img-039-4432bd64.svg", label: "Free delivery" },
              { icon: "/assets/koala/img-040-cf67cad6.svg", label: "120-night trial" },
              { icon: "/assets/koala/img-041-563a3c24.svg", label: "10-year warranty" },
            ]}
            sections={detailSections}
            renderOptions={() => (
              <>
                <fieldset class="hero__choice">
                  <legend>Size <strong>{size()}"</strong></legend>
                  <div class="hero__choices">
                    <For each={["75", "99"]}>
                      {(option) => (
                        <button
                          type="button"
                          class="hero__choice-button"
                          classList={{ "is-selected": size() === option }}
                          aria-pressed={size() === option}
                          onClick={() => setSize(option)}
                        >
                          {option}"
                        </button>
                      )}
                    </For>
                  </div>
                </fieldset>

                <fieldset class="hero__choice hero__choice--colour">
                  <legend>Colour <strong>{colours[colour()].name}</strong></legend>
                  <div class="hero__swatches">
                    <For each={colours}>
                      {(option, index) => (
                        <button
                          type="button"
                          class="hero__swatch"
                          classList={{ "is-selected": colour() === index() }}
                          aria-label={option.name}
                          aria-pressed={colour() === index()}
                          onClick={() => setColour(index())}
                        >
                          <img src={option.src} alt="" aria-hidden="true" />
                        </button>
                      )}
                    </For>
                  </div>
                </fieldset>
              </>
            )}
          />
        </div>
      </div>
    </section>
  );
}

export default HeroSection;
