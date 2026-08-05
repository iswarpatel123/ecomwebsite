import { For, Show, type JSXElement } from "solid-js";
import "./trust-tile.css";

export type TrustTileItem = {
  id: string;
  label: string;
  /** Optional short supporting line under the label. */
  description?: string;
  /** Icon image URL (SVG/PNG). */
  iconSrc?: string;
  iconAlt?: string;
  renderIcon?: () => JSXElement;
};

export type TrustTileProps = {
  items: TrustTileItem[];
  ctaLabel?: string;
  ctaHref?: string;
  onCtaClick?: () => void;
  class?: string;
};

/**
 * Compact trust / policy tile for collection grids.
 * Renders three (or more) clear center-aligned sections — icon above label.
 */
export function TrustTile(props: TrustTileProps) {
  return (
    <aside class={["tt", props.class].filter(Boolean).join(" ")}>
      <ul class="tt__list">
        <For each={props.items}>
          {(item) => (
            <li class="tt__item">
              <div class="tt__icon-wrap">
                <Show when={item.renderIcon} fallback={
                  <Show when={item.iconSrc}>
                    <img class="tt__icon" src={item.iconSrc} alt={item.iconAlt ?? ""} width="32" height="32" />
                  </Show>
                }>
                  {item.renderIcon!()}
                </Show>
              </div>
              <span class="tt__label">{item.label}</span>
              <Show when={item.description}>
                <span class="tt__desc">{item.description}</span>
              </Show>
            </li>
          )}
        </For>
      </ul>
      <Show when={props.ctaLabel}>
        <Show
          when={props.ctaHref}
          fallback={
            <button type="button" class="tt__cta" onClick={() => props.onCtaClick?.()}>
              {props.ctaLabel}
            </button>
          }
        >
          <a class="tt__cta" href={props.ctaHref}>
            {props.ctaLabel}
          </a>
        </Show>
      </Show>
    </aside>
  );
}

export default TrustTile;
