import { For, Show, type JSXElement } from "solid-js";
import "./impact-cards.css";

export type ImpactCard = {
  id: string;
  imageSrc: string;
  imageAlt: string;
  /** Large faded word overlaid near the bottom (e.g. "extinction"). */
  watermark?: string;
  body: string;
  renderFooter?: () => JSXElement;
};

export type ImpactCardsProps = {
  title: string;
  cards: ImpactCard[];
  class?: string;
  id?: string;
};

export function ImpactCards(props: ImpactCardsProps) {
  return (
    <section id={props.id} class={["ic", props.class].filter(Boolean).join(" ")} aria-labelledby="ic-title">
      <h2 id="ic-title" class="ic__title">
        {props.title}
      </h2>
      <ul class="ic__grid">
        <For each={props.cards}>
          {(card) => (
            <li class="ic__card">
              <img class="ic__image" src={card.imageSrc} alt={card.imageAlt} loading="lazy" decoding="async" />
              <div class="ic__overlay">
                <Show when={card.watermark}>
                  <p class="ic__watermark" aria-hidden="true">
                    {card.watermark}
                  </p>
                </Show>
                <p class="ic__body">{card.body}</p>
                <Show when={card.renderFooter}>{card.renderFooter!()}</Show>
              </div>
            </li>
          )}
        </For>
      </ul>
    </section>
  );
}

export default ImpactCards;
