import { Show, type JSXElement } from "solid-js";
import "./newsletter-cta.css";

export type NewsletterCtaProps = {
  title: string;
  buttonLabel?: string;
  href?: string;
  onSubscribe?: () => void;
  renderAction?: () => JSXElement;
  class?: string;
  id?: string;
};

export function NewsletterCta(props: NewsletterCtaProps) {
  return (
    <section id={props.id} class={["nl", props.class].filter(Boolean).join(" ")} aria-labelledby="nl-title">
      <h2 id="nl-title" class="nl__title">
        {props.title}
      </h2>
      <Show
        when={props.renderAction}
        fallback={
          <a
            class="nl__button"
            href={props.href ?? "#"}
            onClick={(e) => {
              if (props.onSubscribe) {
                e.preventDefault();
                props.onSubscribe();
              }
            }}
          >
            {props.buttonLabel ?? "Sign up now"}
          </a>
        }
      >
        {props.renderAction!()}
      </Show>
    </section>
  );
}

export default NewsletterCta;
