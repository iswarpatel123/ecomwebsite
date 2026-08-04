import { ImpactCards } from "@repo/storefront-patterns";
import "./impact-section.css";

export function ImpactSection() {
  return (
    <div class="impact-section">
      <ImpactCards
        title="Cozy home, and a healthy planet"
        cards={[
          {
            id: "wwf",
            imageSrc: "/assets/koala/img-021-488fbda2.png",
            imageAlt: "Koala sleeping in a tree",
            watermark: "extinction",
            body: "Your order helps WWF protect koalas and work toward doubling their numbers by 2050. Over $5.5M donated so far.",
          },
          {
            id: "planet",
            imageSrc: "/assets/koala/img-022-c84ac07f.png",
            imageAlt: "Sunlit forest valley",
            watermark: "1% for the Planet",
            body: "At least 1% of the sales from every order helps environmental causes, and you've helped us donate over $21 million (AUD) to date.",
          },
          {
            id: "bcorp",
            imageSrc: "/assets/koala/img-023-22474324.png",
            imageAlt: "Lush greenery with Certified B Corporation mark",
            watermark: "Corporation",
            body: "We meet the highest standards for social and environmental impact so you can feel good choosing us.",
          },
        ]}
      />
    </div>
  );
}

export default ImpactSection;
