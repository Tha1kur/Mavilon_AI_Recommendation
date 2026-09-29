'use client';

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Sparkles, Search, AlertCircle } from 'lucide-react';
import ContentCard from '@/components/ui/ContentCard';
import { getRecommendations } from '@/lib/api/endpoints';
import { getOrCreateSession } from '@/lib/api/user';
import { Content } from '@/types/content';
import { useApp } from '@/lib/context/app-context';

interface RecommendationWithExplanation {
    content: Content;
    explanation: string;
    score: number;
}

export default function RecommendedSection() {
    const {
        activeSection,
        searchResults,
        selectedMood,
        isSearching,
        searchError,
        searchQuery
    } = useApp();

    const [recommendations, setRecommendations] = useState<RecommendationWithExplanation[]>([]);
    const [loadingRecs, setLoadingRecs] = useState(true);
    const [recError, setRecError] = useState<string | null>(null);

    // Fetch recommendations when mood changes
    useEffect(() => {
        // Don't fetch recs if we are actively searching, unless we want to keep them updated in background?
        // Let's fetch them so if user clears search, they see updated recs.
        async function fetchRecommendations() {
            try {
                setLoadingRecs(true);
                setRecError(null);

                const sessionId = await getOrCreateSession();
                const recs = await getRecommendations(selectedMood || undefined, 6, sessionId);
                setRecommendations(recs);
            } catch (err) {
                console.error('Failed to fetch recommendations:', err);
                setRecError('Failed to load recommendations');
            } finally {
                setLoadingRecs(false);
            }
        }

        fetchRecommendations();
    }, [selectedMood]);

    const showSearch = activeSection === 'search';
    const isLoading = showSearch ? isSearching : loadingRecs;
    const error = showSearch ? searchError : recError;

    const displayItems = showSearch
        ? searchResults.map(c => ({ content: c, explanation: '', score: 0 }))
        : recommendations;

    const title = showSearch
        ? `Results for "${searchQuery}"`
        : selectedMood
            ? `${selectedMood} Picks For You`
            : "Recommended For You";

    if (error) {
        return (
            <section className="py-12 md:py-20 px-4 md:px-8">
                <div className="text-center text-red-400">
                    <p>{error}</p>
                </div>
            </section>
        );
    }

    if (!isLoading && displayItems.length === 0) {
        return (
            <section className="py-12 md:py-20 px-4 md:px-8">
                <div className="text-center text-zinc-500">
                    <p>No content found{showSearch ? ` for "${searchQuery}"` : ''}. Try adjusting your search or filters.</p>
                </div>
            </section>
        );
    }

    return (
        <section className="relative py-16 px-6">
            <div className="max-w-7xl mx-auto">
                {/* Section Header */}
                <motion.div
                    key={showSearch ? 'search-header' : 'rec-header'}
                    initial={{ opacity: 0, x: -50 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.6 }}
                    className="flex items-center gap-3 mb-8"
                >
                    {showSearch ? (
                        <>
                            <Search className="w-8 h-8 text-neon-cyan" />
                            <h2 className="text-4xl font-bold text-white">
                                Results for <span className="text-gradient-cyan">&quot;{searchQuery}&quot;</span>
                            </h2>
                        </>
                    ) : (
                        <>
                            <Sparkles className="w-8 h-8 text-neon-purple" />
                            <h2 className="text-4xl font-bold text-white">
                                {selectedMood ? (
                                    <>
                                        <span className="text-gradient"> {selectedMood}</span> Picks for You
                                    </>
                                ) : (
                                    <>
                                        AI <span className="text-gradient">Recommended</span> for You
                                    </>
                                )}
                            </h2>
                        </>
                    )}
                </motion.div>

                {/* Loading State */}
                {isLoading && (
                    <div className="flex items-center justify-center py-20">
                        <div className="w-12 h-12 border-4 border-neon-purple border-t-transparent rounded-full animate-spin"></div>
                    </div>
                )}

                {/* Error State */}
                {error && (
                    <div className="text-center py-20 flex flex-col items-center gap-4">
                        <AlertCircle className="w-12 h-12 text-red-400" />
                        <p className="text-red-400 text-lg">{error}</p>
                    </div>
                )}

                {/* Empty State */}
                {!isLoading && !error && displayItems.length === 0 && (
                    <div className="text-center py-20">
                        <p className="text-gray-400 text-lg">No content found. Try a different query.</p>
                    </div>
                )}

                {/* Grid */}
                {!isLoading && !error && displayItems.length > 0 && (
                    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
                        {displayItems.map((item, index) => (
                            <ContentCard
                                key={item.content.id}
                                content={item.content}
                                index={index}
                                explanation={item.explanation}
                            />
                        ))}
                    </div>
                )}

                {/* Load More Button - Only for Recs for now */}
                {!showSearch && !isLoading && !error && displayItems.length > 0 && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.6, delay: 0.3 }}
                        className="flex justify-center mt-12"
                    >
                        <button className="px-8 py-4 rounded-full glass-strong hover:shadow-glow-purple transition-all duration-300 group">
                            <span className="flex items-center gap-2 text-white font-medium">
                                <Sparkles className="w-5 h-5 group-hover:text-neon-purple transition-colors" />
                                Discover More
                            </span>
                        </button>
                    </motion.div>
                )}
            </div>
        </section>
    );
}
