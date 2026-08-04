import { Show, type JSXElement } from "solid-js";
import "./media-text.css";

export type MediaTextMedia = {
  type: "image" | "video";
  src: string;
  alt?: string;
  poster?: string;
};

export type MediaTextProps = {
  /** Section eyebrow / kicker above the title. */
  eyebrow?: string;
  title: string;
  body: string;
  /** Place media on the left or right. Default: "right". */
  mediaPosition?: "left" | "right";
  media: MediaTextMedia;
  /** Optional play affordance overlay (visual only when media is video). */
  showPlayAffordance?: boolean;
  /** Slot replacing default media element. */
  renderMedia?: () => JSXElement;
  class?: string;
  id?: string;
};

export function MediaText(props: MediaTextProps) {
  const position = () => props.mediaPosition ?? "right";

  return (
    <article
      id={props.id}
      class={["mt", props.class].filter(Boolean).join(" ")}
      classList={{ "mt--media-left": position() === "left", "mt--media-right": position() === "right" }}
    >
      <div class="mt__copy">
        <Show when={props.eyebrow}>
          <p class="mt__eyebrow">{props.eyebrow}</p>
        </Show>
        <h3 class="mt__title">{props.title}</h3>
        <p class="mt__body">{props.body}</p>
      </div>

      <div class="mt__media">
        <Show when={props.renderMedia} fallback={<DefaultMedia media={props.media} showPlay={props.showPlayAffordance} />}>
          {props.renderMedia!()}
        </Show>
      </div>
    </article>
  );
}

function DefaultMedia(props: { media: MediaTextMedia; showPlay?: boolean }) {
  return (
    <div class="mt__frame">
      <Show
        when={props.media.type === "video"}
        fallback={<img class="mt__asset" src={props.media.src} alt={props.media.alt ?? ""} loading="lazy" decoding="async" />}
      >
        <video
          class="mt__asset"
          src={props.media.src}
          poster={props.media.poster}
          muted
          loop
          playsinline
          autoplay
          aria-label={props.media.alt ?? "Feature video"}
        />
      </Show>
      <Show when={props.showPlay !== false && props.media.type === "video"}>
        <span class="mt__play" aria-hidden="true" />
      </Show>
    </div>
  );
}

export default MediaText;
