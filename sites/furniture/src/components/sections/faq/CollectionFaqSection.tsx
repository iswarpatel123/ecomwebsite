import { Faq, type FaqItem } from "@repo/storefront-patterns";
import "./faq-section.css";

const items: FaqItem[] = [
  {
    id: "what-is-modular",
    question: "What is a modular sofa?",
    answer:
      "A modular sofa is built from separate sections you can rearrange — corner, chaise, loveseat, and ottoman modules that click together so your layout can grow or change with your space.",
    defaultOpen: true,
  },
  {
    id: "reconfigure",
    question: "Can I reconfigure my Bangalow Modular Sofa later?",
    answer:
      "Yes. Modules disconnect and reconnect without tools, so you can switch from an L-shape to a straight sofa, add an ottoman, or flip a chaise as your room changes.",
  },
  {
    id: "covers",
    question: "Are the covers removable and washable?",
    answer:
      "Covers unzip for machine washing on a cold gentle cycle. Tumble dry low or line dry, then re-zip — no dry-cleaning required.",
  },
  {
    id: "delivery",
    question: "How is a modular sofa delivered?",
    answer:
      "Modules ship in manageable boxes with free delivery to most metro areas. Most people assemble in minutes with clear instructions and no tools.",
  },
  {
    id: "returns",
    question: "What is your returns policy?",
    answer:
      "Every sofa includes 120-day free returns. Live with it, rearrange it, and if it is not right we will collect it at no cost.",
  },
];

export function CollectionFaqSection() {
  return (
    <div class="faq-section">
      <Faq title="Modular Sofa FAQs" items={items} />
    </div>
  );
}

export default CollectionFaqSection;
