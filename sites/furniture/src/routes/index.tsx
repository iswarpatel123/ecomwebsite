import { Title } from "@solidjs/meta";
import HeroSection from "../components/sections/hero/HeroSection.jsx";
import FeatureVisualizerSection from "../components/sections/feature-visualizer/FeatureVisualizerSection.jsx";
import BenefitsSection from "../components/sections/benefits/BenefitsSection.jsx";
import ReviewsSection from "../components/sections/reviews/ReviewsSection.jsx";
import FaqSection from "../components/sections/faq/FaqSection.jsx";
import ImpactSection from "../components/sections/impact/ImpactSection.jsx";
import { NewsletterSection, FooterSection } from "../components/sections/site-chrome/SiteChrome.jsx";

export default function Home() {
  return (
    <main class="page">
      <Title>Wanda Sofa Bed – Koala</Title>
      <HeroSection />
      <FeatureVisualizerSection />
      <BenefitsSection />
      <ReviewsSection />
      <FaqSection />
      <ImpactSection />
      <NewsletterSection />
      <FooterSection />
    </main>
  );
}
