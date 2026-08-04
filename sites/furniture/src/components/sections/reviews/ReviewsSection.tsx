import { Reviews, type ReviewItem } from "@repo/storefront-patterns";
import "./reviews-section.css";

const reviews: ReviewItem[] = [
  {
    id: "1",
    author: "Linda R.",
    initials: "LR",
    rating: 5,
    title: "Comfy Sofa Sleeper",
    body: "Fast shipping. With a YouTube video, it's easy enough to assemble. Super comfortable as a sofa and surprisingly great for overnight guests. Covers zip off easily for washing.",
    helpfulYes: 12,
    helpfulNo: 1,
    imageSrc: "/assets/koala/img-004-31bb2a9f.png",
  },
  {
    id: "2",
    author: "Patricia D.",
    initials: "PD",
    rating: 5,
    title: "I love it!!",
    body: "We use it every day in the living room and it has already hosted two weekend guests. Firm enough to sit upright, soft enough to nap. Colour is exactly as shown.",
    helpfulYes: 9,
    helpfulNo: 1,
    imageSrc: "/assets/koala/img-001-8d40340b.png",
  },
  {
    id: "3",
    author: "Sam S.",
    initials: "SS",
    rating: 5,
    title: "Perfect sofa",
    body: "Looks premium, feels premium. The flip-to-bed action is genuinely one motion. Delivery team were careful and the packaging was thoughtful.",
    helpfulYes: 6,
    helpfulNo: 0,
  },
  {
    id: "4",
    author: "Kai H.",
    initials: "KH",
    rating: 4,
    title: "Even better!",
    body: "Took the full 120 days to decide and we kept it. Only note: measure your doorways — the boxes are manageable but not tiny.",
    helpfulYes: 4,
    helpfulNo: 0,
    imageSrc: "/assets/koala/img-008-9b032ead.png",
  },
];

export function ReviewsSection() {
  return (
    <div class="reviews-section">
      <Reviews
        averageRating={4.8}
        totalCount={2085}
        ratingBreakdown={[1800, 258, 18, 10, 9]}
        recommendPercent={98}
        reviews={reviews}
        initiallyVisible={3}
      />
    </div>
  );
}

export default ReviewsSection;
