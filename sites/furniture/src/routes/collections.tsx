import { Title } from "@solidjs/meta";
import CollectionSection from "../components/sections/collection/CollectionSection.jsx";
import ReviewsSection from "../components/sections/reviews/ReviewsSection.jsx";
import CollectionFaqSection from "../components/sections/faq/CollectionFaqSection.jsx";
import { NewsletterSection, FooterSection } from "../components/sections/site-chrome/SiteChrome.jsx";

export default function CollectionsPage() {
  return (
    <main class="page">
      <Title>Bangalow Modular Sofas – Koala</Title>
      <CollectionSection />
      <ReviewsSection />
      <CollectionFaqSection />
      <NewsletterSection />
      <FooterSection />
    </main>
  );
}
