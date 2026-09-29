'use client';

import { motion } from 'framer-motion';
import { ChevronDown, User } from 'lucide-react';
import Link from 'next/link';
import Logo from '@/components/ui/Logo';
import SearchBar from '@/components/ui/SearchBar';
import MoodSelector from '@/components/ui/MoodSelector';
import ContentToggle from '@/components/ui/ContentToggle';

export default function HeroSection() {
    const scrollToContent = () => {
        window.scrollTo({
            top: window.innerHeight,
            behavior: 'smooth',
        });
    };

    return (
        <section className="relative min-h-screen flex flex-col items-center justify-center px-6 py-12">
            {/* Top Navigation / Actions */}
            <div className="absolute top-6 right-6 z-50">
                <Link href="/profile" className="flex items-center gap-2 px-4 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-full backdrop-blur-md transition-all">
                    <div className="w-6 h-6 rounded-full bg-gradient-to-tr from-neon-cyan to-neon-purple flex items-center justify-center">
                        <User className="w-3 h-3 text-white" />
                    </div>
                    <span className="text-sm font-medium text-white">AI Profile</span>
                </Link>
            </div>

            {/* Logo */}
            <Logo size="large" />

            {/* Tagline */}
            <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.8, delay: 0.3 }}
                className="text-xl md:text-2xl text-gray-300 text-center mt-4 mb-12"
            >
                Discover Stories with Intelligence
            </motion.p>

            {/* Search Bar */}
            <div className="w-full mb-12">
                <SearchBar />
            </div>

            {/* Mood Selector */}
            <div className="w-full mb-8">
                <MoodSelector />
            </div>

            {/* Content Toggle */}
            <ContentToggle />

            {/* Scroll Indicator */}
            <motion.button
                initial={{ opacity: 0 }}
                animate={{ opacity: 1, y: [0, 10, 0] }}
                transition={{
                    opacity: { duration: 1, delay: 1 },
                    y: { duration: 2, repeat: Infinity, ease: 'easeInOut' },
                }}
                onClick={scrollToContent}
                className="absolute bottom-12 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 text-gray-400 hover:text-neon-cyan transition-colors cursor-pointer"
            >
                <span className="text-sm">Explore</span>
                <ChevronDown className="w-6 h-6" />
            </motion.button>
        </section>
    );
}
