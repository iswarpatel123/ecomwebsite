import { TabbedMedia, type TabbedMediaTab } from "@repo/storefront-patterns";
import "./feature-visualizer.css";


const VIDEO = "/assets/koala/videos/koala-video.mp4";

const tabs: TabbedMediaTab[] = [
  {
    id: "sits",
    label: "How it sits",
    media: {
      type: "video",
      src: VIDEO,
      poster: "/assets/koala/img-017-7fbc8168.png",
      alt: "Person sitting on the Wanda Sofa Bed",
    },
    people: [
      {
        id: "rob",
        label: "Rob – 6'",
        media: {
          type: "video",
          src: VIDEO,
          poster: "/assets/koala/img-017-7fbc8168.png",
          alt: "Rob sitting on the Wanda Sofa Bed",
        },
      },
      {
        id: "deb",
        label: "Deb – 5'8\"",
        media: {
          type: "image",
          src: "/assets/koala/img-005-9c1f89ac.png",
          alt: "Deb sitting on the Wanda Sofa Bed",
        },
      },
      {
        id: "jen",
        label: "Jen – 5'4\"",
        media: {
          type: "image",
          src: "/assets/koala/img-006-553b3ba8.png",
          alt: "Jen sitting on the Wanda Sofa Bed",
        },
      },
    ],
  },
  {
    id: "sleeps",
    label: "How it sleeps",
    media: {
      type: "video",
      src: VIDEO,
      poster: "/assets/koala/img-002-4cf4af0e.png",
      alt: "Wanda Sofa Bed in bed mode",
    },
  },
  {
    id: "seat-tech",
    label: "Seat tech",
    media: {
      type: "image",
      src: "/assets/koala/img-003-55b0da30.png",
      alt: "Close-up of Wanda Sofa Bed seating",
    },
  },
  {
    id: "sleep-tech",
    label: "Sleep tech",
    media: {
      type: "image",
      src: "/assets/koala/img-007-c460d576.png",
      alt: "Wanda Sofa Bed sleep surface detail",
    },
  },
];

export function FeatureVisualizerSection() {
  return (
    <div class="feature-visualizer">
      <TabbedMedia
        id="feature-visualizer"
        eyebrow="Koala Sofa Bed [4th Gen]"
        title="One flip from sofa to sleep."
        tabs={tabs}
        renderMediaAction={() => (
          <a class="feature-visualizer__specs" href="#faq">
            View size / specs
          </a>
        )}
      />
    </div>
  );
}

export default FeatureVisualizerSection;
