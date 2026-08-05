import { For, Show, createSignal, type JSXElement } from "solid-js";
import "./product-card.css";

export type ProductCardSwatch = {
  name: string;
  /** Image URL for fabric/colour swatch. */
  src?: string;
  /** Solid colour fallback when no swatch image. */
  color?: string;
};

export type ProductCardImage = {
  src: string;
  alt: string;
};

export type ProductCardProps = {
  href: string;
  title: string;
  /** Secondary line (e.g. "2 Sections • 12 Sizes"). */
  subtitle?: string;
  images: ProductCardImage[];
  rating?: number;
  reviewCount?: number;
  price: string;
  compareAtPrice?: string;
  /** e.g. "SAVE $200" */
  saveLabel?: string;
  swatches?: ProductCardSwatch[];
  /** Slot replacing the media carousel. */
  renderMedia?: () => JSXElement;
  class?: string;
};

function stars(n: number) {
  const filled = Math.round(Math.min(5, Math.max(0, n)));
  return "★".repeat(filled) + "☆".repeat(5 - filled);
}

/**
 * Collection product tile. Pass images/text/prices — links via `href`.
 * Image dots cycle locally; no filter/sort logic.
 */
export function ProductCard(props: ProductCardProps) {
  const [index, setIndex] = createSignal(0);
  const images = () => props.images;
  const current = () => images()[index()] ?? images()[0];

  const go = (next: number, e: MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    const len = images().length;
    if (len < 2) return;
    setIndex((next + len) % len);
  };

  return (
    <article class={["pc", props.class].filter(Boolean).join(" ")}>
      <a class="pc__link" href={props.href}>
        <Show when={props.renderMedia} fallback={
          <div class="pc__media">
            <Show when={current()}>
              <img class="pc__image" src={current()!.src} alt={current()!.alt} loading="lazy" decoding="async" />
            </Show>
            <Show when={images().length > 1}>
              <div class="pc__dots" role="tablist" aria-label={`${props.title} images`}>
                <For each={images()}>
                  {(_, i) => (
                    <button
                      type="button"
                      class="pc__dot"
                      classList={{ "is-active": index() === i() }}
                      aria-label={`Show image ${i() + 1}`}
                      aria-selected={index() === i()}
                      onClick={(e) => go(i(), e)}
                    />
                  )}
                </For>
              </div>
            </Show>
          </div>
        }>
          {props.renderMedia!()}
        </Show>

        <div class="pc__body">
          <Show when={props.rating !== undefined}>
            <p class="pc__rating">
              <span class="pc__stars" aria-label={`Rated ${props.rating} out of 5`}>
                {stars(props.rating!)}
              </span>
              <Show when={props.reviewCount !== undefined}>
                <span class="pc__count">({props.reviewCount!.toLocaleString()})</span>
              </Show>
            </p>
          </Show>

          <h3 class="pc__title">{props.title}</h3>
          <Show when={props.subtitle}>
            <p class="pc__subtitle">{props.subtitle}</p>
          </Show>

          <div class="pc__price-row">
            <Show when={props.saveLabel}>
              <span class="pc__save">{props.saveLabel}</span>
            </Show>
            <Show when={props.compareAtPrice}>
              <span class="pc__compare">{props.compareAtPrice}</span>
            </Show>
            <span class="pc__price">{props.price}</span>
          </div>

          <Show when={props.swatches && props.swatches.length > 0}>
            <ul class="pc__swatches" aria-label="Available colours">
              <For each={props.swatches!}>
                {(swatch) => (
                  <li>
                    <Show
                      when={swatch.src}
                      fallback={
                        <span
                          class="pc__swatch"
                          style={{ "background-color": swatch.color ?? "#ccc" }}
                          title={swatch.name}
                          aria-label={swatch.name}
                        />
                      }
                    >
                      <img class="pc__swatch pc__swatch--img" src={swatch.src} alt="" title={swatch.name} />
                    </Show>
                  </li>
                )}
              </For>
            </ul>
          </Show>
        </div>
      </a>
    </article>
  );
}

export default ProductCard;
