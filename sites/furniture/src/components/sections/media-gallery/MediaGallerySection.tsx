import { For } from "solid-js";
import { MediaTile, type MediaTileItem } from "./MediaTile.jsx";
import "./media-gallery.css";

/**
 * Desktop product media grid (2 cols × up to 4 rows).
 * Sits under the main hero image in the left column — not a separate page section.
 */
export const mediaItems: MediaTileItem[] = [
  {
    type: "video",
    src: "/assets/koala/videos/koala-video.mp4",
    poster: "/assets/koala/img-024-df90a771.png",
    alt: "a modern sofa bed in multiple different colors",
  },
  {
    type: "image",
    src: "/assets/koala/img-001-8d40340b.png",
    alt: "Wanda Sofa Bed lifestyle — person standing on sofa outdoors",
  },
  {
    type: "image",
    src: "/assets/koala/img-002-4cf4af0e.png",
    alt: "Wanda Sofa Bed shown as a bed",
  },
  {
    type: "image",
    src: "/assets/koala/img-003-55b0da30.png",
    alt: "Wanda Sofa Bed detail",
  },
  {
    type: "image",
    src: "/assets/koala/img-004-31bb2a9f.png",
    alt: "Wanda Sofa Bed in a living room",
  },
  {
    type: "image",
    src: "/assets/koala/img-005-9c1f89ac.png",
    alt: "Wanda Sofa Bed studio front view",
  },
  {
    type: "image",
    src: "/assets/koala/img-006-553b3ba8.png",
    alt: "Wanda Sofa Bed product photograph",
  },
  {
    type: "image",
    src: "/assets/koala/img-007-c460d576.png",
    alt: "Wanda Sofa Bed product photograph",
  },
];

export function MediaGalleryGrid() {
  return (
    <div class="media-gallery__grid" aria-label="Product media gallery">
      <For each={mediaItems}>{(item) => <MediaTile item={item} />}</For>
    </div>
  );
}

export default MediaGalleryGrid;
