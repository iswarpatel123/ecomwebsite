import { Show, type JSXElement } from "solid-js";
import "./quote-tile.css";

export type QuoteTileProps = {
  quote: string;
  author?: string;
  rating?: number;
  /** Optional footer CTA — omit for quote-only tiles. */
  ctaLabel?: string;
  ctaHref?: string;
  renderFooter?: () => JSXElement;
  class?: string;
};

function stars(n: number) {
  const filled = Math.round(Math.min(5, Math.max(0, n)));
  return "★".repeat(filled) + "☆".repeat(5 - filled);
}

/**
 * Single-review / testimonial tile for collection merchandising grids.
 * Default is stars + quote (+ optional author) — no CTA required.
 */
export function QuoteTile(props: QuoteTileProps) {
  return (
    <aside class={["qt", props.class].filter(Boolean).join(" ")}>
      <div class="qt__inner">
        <Show when={props.rating !== undefined}>
          <p class="qt__stars" aria-label={`Rated ${props.rating} out of 5`}>
            {stars(props.rating!)}
          </p>
        </Show>
        <blockquote class="qt__quote">
          <p>“{props.quote}”</p>
          <Show when={props.author}>
            <footer>
              <cite class="qt__author">{props.author}</cite>
            </footer>
          </Show>
        </blockquote>
        <Show when={props.renderFooter}>
          {props.renderFooter!()}
        </Show>
        <Show when={!props.renderFooter && props.ctaLabel && props.ctaHref}>
          <a class="qt__cta" href={props.ctaHref}>
            {props.ctaLabel}
          </a>
        </Show>
      </div>
    </aside>
  );
}

export default QuoteTile;
