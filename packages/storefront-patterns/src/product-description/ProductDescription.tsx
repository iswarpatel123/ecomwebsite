import { For, Show, createSignal, type JSXElement } from "solid-js";
import "./product-description.css";

/* -------------------------------------------------------------------------- */
/* Types                                                                       */
/* -------------------------------------------------------------------------- */

/** Single accordion section displayed in the product details area. */
export type AccordionSection = {
  /** Unique key used for open/close state and aria controls. */
  id: string;
  /** Visible heading text (rendered as-is; support rich markup via renderTitle). */
  title: string;
  /** Static HTML / markdown string shown when expanded. */
  content?: string;
  /** Slot for fully custom content when `content` string isn't enough. */
  renderContent?: () => JSXElement;
  /** Slot for custom title (icon + text, etc.). */
  renderTitle?: () => JSXElement;
  /** Whether this section starts expanded. Default: false. */
  defaultOpen?: boolean;
};

/** Props accepted by <ProductDescription>. */
export type ProductDescriptionProps = {
  /* ---- Product info ---------------------------------------------------- */
  /** Breadcrumb label (e.g. "Sofa Beds"). */
  breadcrumbLabel?: string;
  breadcrumbHref?: string;

  /** Star rating 0–5. */
  rating?: number;
  /** Number of reviews (displayed in parentheses). */
  reviewCount?: number;
  /** Link target for the review count text. */
  reviewHref?: string;

  /** Product name — rendered as <h1>. */
  title: string;

  /** Sale / regular price (displayed as-is, e.g. "$1,950"). */
  price: string;
  /** Optional "was" / original price shown struck through. */
  compareAtPrice?: string;

  /** Payment plan blurb, e.g. "or 4 interest-free payments …". */
  paymentPlan?: string;

  /* ---- Accordion sections ------------------------------------------------ */
  /** Ordered list of detail sections below the buy box. */
  sections?: AccordionSection[];

  /* ---- Benefits bar (optional) ------------------------------------------- */
  benefits?: Array<{ icon?: string; label: string }>;

  /* ---- Purchase controls ------------------------------------------------- */
  /** Rendered above/beside the Add-to-Cart button. */
  renderOptions?: () => JSXElement;
  /** Slot for a fully custom purchase area (replaces default quantity + add-to-cart). */
  renderPurchase?: () => JSXElement;

  /* ---- Children ---------------------------------------------------------- */
  /** Arbitrary content injected between the accordion and the purchase area. */
  children?: JSXElement;

  /* ---- Styling ----------------------------------------------------------- */
  class?: string;
};

/* -------------------------------------------------------------------------- */
/* Component                                                                   */
/* -------------------------------------------------------------------------- */

export function ProductDescription(props: ProductDescriptionProps) {
  return (
    <div class={["pd", props.class].filter(Boolean).join(" ")}>
      {/* Breadcrumb */}
      <Show when={props.breadcrumbLabel}>
        <a class="pd__breadcrumb" href={props.breadcrumbHref ?? "#"}>
          {props.breadcrumbLabel}
        </a>
      </Show>

      {/* Rating */}
      <Show when={props.rating !== undefined}>
        <div
          class="pd__rating"
          aria-label={`Rated ${props.rating} out of 5 stars from ${props.reviewCount ?? 0} reviews`}
        >
          <span aria-hidden="true" class="pd__stars">
            {"★".repeat(Math.round(props.rating!))}
            {"☆".repeat(5 - Math.round(props.rating!))}
          </span>
          <a class="pd__review-link" href={props.reviewHref ?? "#reviews"}>
            ({props.reviewCount ?? 0} Reviews)
          </a>
        </div>
      </Show>

      {/* Title */}
      <h1 class="pd__title">{props.title}</h1>

      {/* Price block */}
      <div class="pd__price-block">
        <span class="pd__price">{props.price}</span>
        <Show when={props.compareAtPrice}>
          <span class="pd__compare-price">{props.compareAtPrice}</span>
        </Show>
      </div>

      <Show when={props.paymentPlan}>
        <p class="pd__payment-plan">{props.paymentPlan}</p>
      </Show>

      {/* Benefits */}
      <Show when={props.benefits && props.benefits.length > 0}>
        <div class="pd__benefits" aria-label="Purchase benefits">
          <For each={props.benefits!}>
            {(b) => (
              <div class="pd__benefit">
                <Show when={b.icon}>
                  <img src={b.icon!} alt="" aria-hidden="true" />
                </Show>
                <span>{b.label}</span>
              </div>
            )}
          </For>
        </div>
      </Show>

      {/* Options / selectors */}
      <Show when={props.renderOptions}>
        <div class="pd__options">{props.renderOptions!()}</div>
      </Show>

      {/* Purchase area */}
      <Show when={props.renderPurchase} fallback={<DefaultPurchase price={props.price} />}>
        {props.renderPurchase!()}
      </Show>

      {/* Accordion sections */}
      <Show when={props.sections && props.sections.length > 0}>
        <div class="pd__accordion" role="list">
          <For each={props.sections!}>
            {(section) => <AccordionItem section={section} />}
          </For>
        </div>
      </Show>

      {/* Slot for arbitrary extra content */}
      {props.children}
    </div>
  );
}

/* -------------------------------------------------------------------------- */
/* AccordionItem (internal)                                                    */
/* -------------------------------------------------------------------------- */

function AccordionItem(props: { section: AccordionSection }) {
  const [open, setOpen] = createSignal(props.section.defaultOpen ?? false);
  const panelId = `pd-panel-${props.section.id}`;
  const triggerId = `pd-trigger-${props.section.id}`;

  return (
    <div class="pd__accordion-item" classList={{ "is-open": open() }}>
      <button
        id={triggerId}
        class="pd__accordion-trigger"
        type="button"
        aria-expanded={open()}
        aria-controls={panelId}
        onClick={() => setOpen((o) => !o)}
      >
        <span class="pd__accordion-title">
          {props.section.renderTitle
            ? props.section.renderTitle()
            : props.section.title}
        </span>
        <span class="pd__accordion-icon" aria-hidden="true">
          {open() ? "−" : "+"}
        </span>
      </button>
      <div
        id={panelId}
        class="pd__accordion-panel"
        role="region"
        aria-labelledby={triggerId}
        hidden={!open()}
      >
        <Show
          when={props.section.renderContent}
          fallback={
            <div class="pd__accordion-content" innerHTML={props.section.content ?? ""} />
          }
        >
          {props.section.renderContent!()}
        </Show>
      </div>
    </div>
  );
}

/* -------------------------------------------------------------------------- */
/* DefaultPurchase (fallback)                                                   */
/* -------------------------------------------------------------------------- */

function DefaultPurchase(props: { price: string }) {
  const [qty, setQty] = createSignal(1);
  const [added, setAdded] = createSignal(false);

  const addToCart = () => {
    setAdded(true);
    window.setTimeout(() => setAdded(false), 2400);
  };

  return (
    <div class="pd__purchase">
      <div class="pd__quantity" aria-label="Quantity">
        <button type="button" aria-label="Decrease quantity" onClick={() => setQty((q) => Math.max(1, q - 1))} disabled={qty() === 1}>
          −
        </button>
        <output aria-live="polite">{qty()}</output>
        <button type="button" aria-label="Increase quantity" onClick={() => setQty((q) => Math.min(10, q + 1))} disabled={qty() === 10}>
          +
        </button>
      </div>
      <button class="pd__add-to-cart" type="button" onClick={addToCart}>
        {added() ? "Added to cart" : `Add to cart • ${props.price}`}
      </button>
    </div>
  );
}

/* Re-export types for consumers */
export type { ProductDescriptionProps as PDProps };
