import type { JSX } from "solid-js";

export type MediaTileItem = {
  type: "image" | "video";
  src: string;
  alt?: string;
  /** Poster frame for video tiles */
  poster?: string;
};

type MediaTileProps = {
  item: MediaTileItem;
  class?: string;
};

/**
 * Single gallery cell that renders either an image or a video.
 * Reused for every slot in the under-hero media grid.
 */
export function MediaTile(props: MediaTileProps): JSX.Element {
  const item = () => props.item;

  return (
    <figure class={`media-tile ${props.class ?? ""}`.trim()}>
      {item().type === "video" ? (
        <video
          class="media-tile__media"
          src={item().src}
          poster={item().poster}
          muted
          loop
          playsinline
          autoplay
          aria-label={item().alt ?? "Product video"}
        />
      ) : (
        <img class="media-tile__media" src={item().src} alt={item().alt ?? ""} loading="lazy" decoding="async" />
      )}
    </figure>
  );
}

export default MediaTile;
