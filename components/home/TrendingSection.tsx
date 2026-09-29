'use client';

import { useRef, useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { ChevronLeft, ChevronRight, TrendingUp } from 'lucide-react';
import ContentCard from '@/components/ui/ContentCard';
import { getTrendingMovies, getTrendingAnime } from '@/lib/api/endpoints';
import { Content } from '@/types/content';


export default function TrendingSection() {
    const scrollRef = useRef<HTMLDivElement>(null);
    const [content, setContent] = useState<Content[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        async function fetchTrending() {
            try {
                setLoading(true);
                setError(null);

                // Fetch both movies and anime in parallel
                const [movies, anime] = await Promise.all([
                    getTrendingMovies(10),
                    getTrendingAnime(10)
                ]);

                // Mix movies and anime, alternating
                const mixed: Content[] = [];
                const maxLength = Math.max(movies.length, anime.length);

                for (let i = 0; i < maxLength; i++) {
                    if (i < movies.length) mixed.push(movies[i]);
                    if (i < anime.length) mixed.push(anime[i]);
                }

                setContent(mixed.slice(0, 12)); // Limit to 12 items
            } catch (err) {
                console.error('Failed to fetch trending content:', err);
                setError('Failed to load trending content');
            } finally {
                setLoading(false);
            }
        }

        fetchTrending();
    }, []);

    const scroll = (direction: 'left' | 'right') => {
        if (scrollRef.current) {
            const scrollAmount = 400;
            scrollRef.current.scrollBy({
                left: direction === 'left' ? -scrollAmount : scrollAmount,
                behavior: 'smooth',
            });
        }
    };

    return (
        <section className="relative py-16 px-6">
            <div className="max-w-7xl mx-auto">
                {/* Section Header */}
                <motion.div
                    initial={{ opacity: 0, x: -50 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.6 }}
                    className="flex items-center gap-3 mb-8"
                >
                    <TrendingUp className="w-8 h-8 text-neon-cyan" />
                    <h2 className="text-4xl font-bold text-white">
                        Trending <span className="text-gradient">Now</span>
                    </h2>
                </motion.div>

                {/* Loading State */}
                {loading && (
                    <div className="flex items-center justify-center py-20">
                        <div className="w-12 h-12 border-4 border-neon-cyan border-t-transparent rounded-full animate-spin"></div>
                    </div>
                )}

                {/* Error State */}
                {error && (
                    <div className="text-center py-20">
                        <p className="text-red-400">{error}</p>
                    </div>
                )}

                {/* Carousel Container */}
                {!loading && !error && content.length > 0 && (
                    <div className="relative group">
                        {/* Left Arrow */}
                        <button
                            onClick={() => scroll('left')}
                            className="absolute left-0 top-1/2 -translate-y-1/2 z-20 p-3 rounded-full glass-strong opacity-0 group-hover:opacity-100 transition-opacity hover:bg-neon-cyan/20"
                        >
                            <ChevronLeft className="w-6 h-6 text-white" />
                        </button>

                        {/* Right Arrow */}
                        <button
                            onClick={() => scroll('right')}
                            className="absolute right-0 top-1/2 -translate-y-1/2 z-20 p-3 rounded-full glass-strong opacity-0 group-hover:opacity-100 transition-opacity hover:bg-neon-cyan/20"
                        >
                            <ChevronRight className="w-6 h-6 text-white" />
                        </button>

                        {/* Scrollable Content */}
                        <div
                            ref={scrollRef}
                            className="flex gap-6 overflow-x-auto scrollbar-hide scroll-smooth pb-4"
                            style={{
                                scrollbarWidth: 'none',
                                msOverflowStyle: 'none',
                            }}
                        >
                            {content.map((item, index) => (
                                <div key={item.id} className="flex-shrink-0 w-72">
                                    <ContentCard content={item} index={index} />
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </section>
    );
}
