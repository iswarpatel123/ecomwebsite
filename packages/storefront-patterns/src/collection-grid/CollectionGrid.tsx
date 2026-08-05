import { For, Show, type JSXElement } from "solid-js";
import { ProductCard, type ProductCardProps } from "../product-card/ProductCard";
import { PromoMediaTile, type PromoMediaTileProps } from "../promo-media-tile/PromoMediaTile";
import { QuoteTile, type QuoteTileProps } from "../quote-tile/QuoteTile";
import { TrustTile, type TrustTileProps } from "../trust-tile/TrustTile";
import "./collection-grid.css";

export type CollectionProductItem = {
  type: "product";
  id: string;
  product: ProductCardProps;
};

export type CollectionPromoItem = {
  type: "promo";
  id: string;
  promo: PromoMediaTileProps;
};

export type CollectionQuoteItem = {
  type: "quote";
  id: string;
  quote: QuoteTileProps;
};

export type CollectionTrustItem = {
  type: "trust";
  id: string;
  trust: TrustTileProps;
};

export type CollectionCustomItem = {
  type: "custom";
  id: string;
  render: () => JSXElement;
};

export type CollectionGridItem =
  | CollectionProductItem
  | CollectionPromoItem
  | CollectionQuoteItem
  | CollectionTrustItem
  | CollectionCustomItem;

export type CollectionGridProps = {
  title: string;
  items: CollectionGridItem[];
  /** Optional heading slot (e.g. custom title + controls). */
  renderHeader?: () => JSXElement;
  class?: string;
  id?: string;
};

function GridCell(props: { item: CollectionGridItem }) {
  const item = props.item;
  if (item.type === "product") return <ProductCard {...item.product} />;
  if (item.type === "promo") return <PromoMediaTile {...item.promo} />;
  if (item.type === "quote") return <QuoteTile {...item.quote} />;
  if (item.type === "trust") return <TrustTile {...item.trust} />;
  return item.render();
}

/**
 * Mixed collection merchandising grid.
 * Items are a discriminated union — swap props per tile; site owns data.
 */
export function CollectionGrid(props: CollectionGridProps) {
  return (
    <section id={props.id} class={["cg", props.class].filter(Boolean).join(" ")} aria-labelledby="cg-title">
      <Show
        when={props.renderHeader}
        fallback={
          <header class="cg__header">
            <h1 id="cg-title" class="cg__title">
              {props.title}
            </h1>
          </header>
        }
      >
        {props.renderHeader!()}
      </Show>

      <ul class="cg__grid">
        <For each={props.items}>
          {(item) => (
            <li class="cg__cell" data-type={item.type}>
              <GridCell item={item} />
            </li>
          )}
        </For>
      </ul>
    </section>
  );
}

export default CollectionGrid;
