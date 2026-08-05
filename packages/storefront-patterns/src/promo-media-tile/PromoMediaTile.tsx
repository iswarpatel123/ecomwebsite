import { Show, createSignal, type JSXElement } from "solid-js";
import "./promo-media-tile.css";

export type PromoMediaTileProps = {
  title: string;
  /** Poster / still image shown before play. */
  imageSrc: string;
  imageAlt?: string;
  /** Local or remote video; click-to-play when provided. */
  videoSrc?: string;
  ctaLabel?: string;
  ctaHref?: string;
  /** Slot for custom overlay copy. */
  renderOverlay?: () => JSXElement;
  class?: string;
};

/**
 * Merchandising grid tile with optional click-to-play video.
 * Swap `imageSrc` / `videoSrc` / copy via props — no site-specific logic.
 */
export function PromoMediaTile(props: PromoMediaTileProps) {
  const [playing, setPlaying] = createSignal(false);
  let videoEl: HTMLVideoElement | undefined;

  const startPlayback = async () => {
    if (!props.videoSrc) return;
    setPlaying(true);
    queueMicrotask(async () => {
      try {
        await videoEl?.play();
      } catch {
        /* autoplay policies — user already clicked */
      }
    });
  };

  return (
    <article class={["pm", props.class].filter(Boolean).join(" ")}>
      <div class="pm__frame">
        <Show
          when={playing() && props.videoSrc}
          fallback={<img class="pm__media" src={props.imageSrc} alt={props.imageAlt ?? ""} loading="lazy" decoding="async" />}
        >
          <video
            ref={(el) => {
              videoEl = el;
            }}
            class="pm__media"
            src={props.videoSrc}
            poster={props.imageSrc}
            controls
            playsinline
            aria-label={props.imageAlt ?? props.title}
          />
        </Show>

        <Show when={!playing()}>
          <div class="pm__overlay">
            <Show when={props.renderOverlay} fallback={<h3 class="pm__title">{props.title}</h3>}>
              {props.renderOverlay!()}
            </Show>

            <div class="pm__actions">
              <Show when={props.videoSrc}>
                <button type="button" class="pm__play" aria-label={`Play video: ${props.title}`} onClick={() => void startPlayback()}>
                  <span class="pm__play-icon" aria-hidden="true" />
                </button>
              </Show>
              <Show when={props.ctaLabel && props.ctaHref}>
                <a class="pm__cta" href={props.ctaHref}>
                  {props.ctaLabel}
                </a>
              </Show>
            </div>
          </div>
        </Show>
      </div>
    </article>
  );
}

export default PromoMediaTile;
