import HeroSection from '@/components/home/HeroSection';
import TrendingSection from '@/components/home/TrendingSection';
import RecommendedSection from '@/components/home/RecommendedSection';

export default function Home() {
    return (
        <main className="min-h-screen">
            <HeroSection />
            <TrendingSection />
            <RecommendedSection />
        </main>
    );
}
