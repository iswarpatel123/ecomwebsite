import { Faq, type FaqItem } from "@repo/storefront-patterns";
import "./faq-section.css";

const items: FaqItem[] = [
  {
    id: "comfort",
    question: "What makes the Koala Sofa Bed 4th Gen so comfortable to sleep on?",
    answer:
      "It uses the same CloudCell™ comfort technology as our mattresses — a full-size sleep surface with no bars or springs digging into your back when you flip from sofa to bed.",
    defaultOpen: true,
  },
  {
    id: "fabrics",
    question: "What makes Koala's fabrics exclusive?",
    answer:
      "Our performance fabrics are developed for real homes: water-resistant, stain-resistant, soft to the touch, and available in eight colours engineered for daily wear with kids and pets.",
  },
  {
    id: "wash",
    question: "How should I wash the covers to keep my sofa bed looking as good as new?",
    answer:
      "Unzip the covers, machine wash cold on a gentle cycle, then tumble dry low or line dry. Re-zip and fluff — no dry-cleaning required.",
  },
  {
    id: "tools",
    question: "Do I need tools to assemble my sofa bed?",
    answer:
      "No. Everything click-fits together with clear instructions in the box. Most people finish setup in minutes without tools or a handyman.",
  },
  {
    id: "covers",
    question: "Can I purchase additional or replacement covers separately?",
    answer:
      "Yes. Extra covers are available so you can refresh your look or keep a spare set on rotation while one is in the wash.",
  },
];

export function FaqSection() {
  return (
    <div class="faq-section">
      <Faq items={items} />
    </div>
  );
}

export default FaqSection;
