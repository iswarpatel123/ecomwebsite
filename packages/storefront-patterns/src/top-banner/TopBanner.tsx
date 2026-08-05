import { For, Show, createSignal, onCleanup, onMount, type JSXElement } from "solid-js";
import "./top-banner.css";

export type TopBannerLink = {
  label: string;
  href: string;
};

export type TopBannerProps = {
  /** Single announcement (used when `messages` is omitted). */
  message?: string;
  /** Rotating announcements — preferred over `message` when provided. */
  messages?: string[];
  /** Rotation interval in ms. Default: 4000. Ignored for a single message. */
  intervalMs?: number;
  /** Optional utility links pinned to the right (Help, Contact, …). */
  links?: TopBannerLink[];
  /** Slot replacing the default message text. */
  renderMessage?: () => JSXElement;
  /** Slot replacing the default links row. */
  renderLinks?: () => JSXElement;
  class?: string;
  id?: string;
};

/**
 * Non-sticky announcement strip. Message is center-aligned;
 * optional `messages` rotate on an interval. Scrolls away with the page.
 */
export function TopBanner(props: TopBannerProps) {
  const list = () => {
    if (props.messages && props.messages.length > 0) return props.messages;
    if (props.message) return [props.message];
    return [] as string[];
  };

  const [index, setIndex] = createSignal(0);
  const [fade, setFade] = createSignal(true);

  onMount(() => {
    const items = list();
    if (items.length < 2) return;
    const ms = props.intervalMs ?? 4000;
    let fadeTimer = 0;
    const id = window.setInterval(() => {
      setFade(false);
      window.clearTimeout(fadeTimer);
      fadeTimer = window.setTimeout(() => {
        setIndex((i) => (i + 1) % items.length);
        setFade(true);
      }, 220);
    }, ms);
    onCleanup(() => {
      window.clearInterval(id);
      window.clearTimeout(fadeTimer);
    });
  });

  const current = () => list()[index()] ?? "";

  return (
    <div id={props.id} class={["tb", props.class].filter(Boolean).join(" ")} role="region" aria-label="Site announcement" aria-live="polite">
      <div class="tb__inner">
        <Show when={props.renderMessage} fallback={
          <p class="tb__message" classList={{ "is-in": fade(), "is-out": !fade() }}>
            {current()}
          </p>
        }>
          {props.renderMessage!()}
        </Show>

        <Show when={props.renderLinks} fallback={
          <Show when={props.links && props.links.length > 0}>
            <ul class="tb__links">
              <For each={props.links!}>
                {(link) => (
                  <li>
                    <a href={link.href}>{link.label}</a>
                  </li>
                )}
              </For>
            </ul>
          </Show>
        }>
          {props.renderLinks!()}
        </Show>
      </div>
    </div>
  );
}

export default TopBanner;
