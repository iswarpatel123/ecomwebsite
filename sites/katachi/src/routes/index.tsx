import { Title } from "@solidjs/meta";
import HeroSection from "../components/sections/hero/HeroSection.jsx";

export default function Home() {
  return (
    <>
      <Title>KATACHI Studio</Title>
      <main class="min-h-screen">
        <HeroSection />
      </main>
    </>
  );
}
