import { For } from "solid-js";
import { MediaText, type MediaTextProps } from "@repo/storefront-patterns";
import "./benefits.css";

const VIDEO = "/assets/koala/videos/koala-video.mp4";

const rows: MediaTextProps[] = [
  {
    title: "Try it risk-free. 120 days.",
    body: "Buy with complete confidence. Every Wanda Sofa Bed comes with 120-day free returns. That's four months to live on it, sleep on it, and love it. If it's not right, we'll collect it for free. No awkward returns, no restocking fees, no stress.",
    mediaPosition: "right",
    media: {
      type: "video",
      src: VIDEO,
      poster: "/assets/koala/img-025-f928d801.png",
      alt: "Friends assembling and lounging on a sofa bed",
    },
  },
  {
    title: "Fabrics built for real life.",
    body: "Koala's covers are water-resistant, stain-resistant, and removable because life happens. When it does, just unzip, toss in the machine, and zip back on. No dry-cleaning, no professional upholstery, no drama. Eight color options, all engineered to handle kids, pets, and daily use without losing their look.",
    mediaPosition: "left",
    media: {
      type: "video",
      src: VIDEO,
      poster: "/assets/koala/img-028-1ccf9fab.png",
      alt: "Close-up of sofa bed fabric colours",
    },
  },
  {
    title: "Ultimate comfort. Day and night.",
    body: "We've taken our signature CloudCell™ comfort technology, perfected in Australia's favourite mattresses, and built it into a sofa. Deep seats feel incredible for everyday lounging, then flip it flat and get a proper night's sleep on a full-size Koala mattress. No bars. No springs. Just real rest.",
    mediaPosition: "right",
    media: {
      type: "video",
      src: VIDEO,
      poster: "/assets/koala/img-027-f51993a4.png",
      alt: "Person and dog resting on a sofa bed",
    },
  },
  {
    title: "Set up in minutes. No tools needed.",
    body: "Your Wanda Sofa Bed arrives ready to assemble in minutes. No tools, no handyman, no YouTube tutorials. Clear instructions, click-together components, and everything you need is in the box — so you can go from delivery to lounging before dinner.",
    mediaPosition: "left",
    media: {
      type: "video",
      src: VIDEO,
      poster: "/assets/koala/img-029-76a09829.png",
      alt: "Friends opening storage under a sofa bed",
    },
  },
];

export function BenefitsSection() {
  return (
    <section class="benefits" aria-labelledby="benefits-title">
      <header class="benefits__header">
        <p class="benefits__eyebrow">Why the Koala Sofa Bed?</p>
        <h2 id="benefits-title" class="benefits__title">
          Comfort, without compromise
        </h2>
      </header>

      <div class="benefits__rows">
        <For each={rows}>{(row) => <MediaText {...row} />}</For>
      </div>
    </section>
  );
}

export default BenefitsSection;
