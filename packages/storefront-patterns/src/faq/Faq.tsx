import { For, Show, createSignal, type JSXElement } from "solid-js";
import "./faq.css";

export type FaqItem = {
  id: string;
  question: string;
  answer: string;
  renderAnswer?: () => JSXElement;
  defaultOpen?: boolean;
};

export type FaqProps = {
  title?: string;
  items: FaqItem[];
  class?: string;
  id?: string;
};

export function Faq(props: FaqProps) {
  return (
    <section id={props.id ?? "faq"} class={["faq", props.class].filter(Boolean).join(" ")} aria-labelledby="faq-title">
      <h2 id="faq-title" class="faq__title">
        {props.title ?? "Frequently asked questions"}
      </h2>
      <div class="faq__list" role="list">
        <For each={props.items}>{(item) => <FaqRow item={item} />}</For>
      </div>
    </section>
  );
}

function FaqRow(props: { item: FaqItem }) {
  const [open, setOpen] = createSignal(props.item.defaultOpen ?? false);
  const panelId = `faq-panel-${props.item.id}`;
  const triggerId = `faq-trigger-${props.item.id}`;

  return (
    <div class="faq__item" classList={{ "is-open": open() }} role="listitem">
      <button
        id={triggerId}
        type="button"
        class="faq__trigger"
        aria-expanded={open()}
        aria-controls={panelId}
        onClick={() => setOpen((v) => !v)}
      >
        <span>{props.item.question}</span>
        <span class="faq__icon" aria-hidden="true">
          {open() ? "−" : "+"}
        </span>
      </button>
      <div id={panelId} class="faq__panel" role="region" aria-labelledby={triggerId} hidden={!open()}>
        <Show when={props.item.renderAnswer} fallback={<p class="faq__answer">{props.item.answer}</p>}>
          {props.item.renderAnswer!()}
        </Show>
      </div>
    </div>
  );
}

export default Faq;
