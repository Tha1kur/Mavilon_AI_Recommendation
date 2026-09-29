'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Star, Play, Calendar, Clock, Film } from 'lucide-react';
import Image from 'next/image';
import { Content } from '@/types/content';
import { getContentDetails } from '@/lib/api/endpoints';
import ContentCard from '@/components/ui/ContentCard';

interface ContentDetailsModalProps {
    contentId: string;
    contentType: 'movie' | 'anime';
    isOpen: boolean;
    onClose: () => void;
}

export default function ContentDetailsModal({ contentId, contentType, isOpen, onClose }: ContentDetailsModalProps) {
    const [details, setDetails] = useState<Content | null>(null);
    const [similar, setSimilar] = useState<Content[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [showTrailer, setShowTrailer] = useState(false);

    useEffect(() => {
        if (!isOpen) {
            // Reset state when closed
            setTimeout(() => {
                setDetails(null);
                setSimilar([]);
                setError(null);
                setLoading(true);
                setShowTrailer(false);
            }, 300);
            return;
        }

        let isMounted = true;

        async function fetchData() {
            setLoading(true);
            setError(null);
            try {
                const detailsData = await getContentDetails(contentType, contentId);

                if (isMounted) {
                    setDetails(detailsData);
                    setSimilar(detailsData.similar || []);
                }
            } catch (err) {
                console.error('Failed to fetch content details:', err);
                if (isMounted) setError('Failed to load details.');
            } finally {
                if (isMounted) setLoading(false);
            }
        }

        fetchData();

        return () => {
            isMounted = false;
        };
    }, [isOpen, contentId, contentType]);

    // Close on escape key
    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if (e.key === 'Escape') onClose();
        };
        if (isOpen) window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [isOpen, onClose]);

    return (
        <AnimatePresence>
            {isOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6">
                    {/* Backdrop */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={onClose}
                        className="absolute inset-0 bg-black/80 backdrop-blur-sm"
                    />

                    {/* Modal Content */}
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95, y: 20 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95, y: 20 }}
                        className="relative w-full max-w-5xl max-h-[90vh] overflow-y-auto bg-dark-800 rounded-2xl shadow-2xl border border-white/10"
                        onClick={(e) => e.stopPropagation()}
                    >
                        {/* Close Button */}
                        <button
                            onClick={onClose}
                            className="absolute top-4 right-4 z-20 p-2 bg-black/50 hover:bg-black/80 text-white rounded-full backdrop-blur-md transition-colors"
                        >
                            <X className="w-6 h-6" />
                        </button>

                        {loading ? (
                            <div className="flex flex-col items-center justify-center min-h-[400px] gap-4">
                                <div className="w-12 h-12 border-4 border-neon-cyan border-t-transparent rounded-full animate-spin"></div>
                                <span className="text-gray-400">Loading details...</span>
                            </div>
                        ) : error ? (
                            <div className="flex flex-col items-center justify-center min-h-[400px] gap-4 px-6 text-center">
                                <span className="text-red-400 text-lg">{error}</span>
                                <button onClick={onClose} className="px-6 py-2 bg-white/10 rounded-lg hover:bg-white/20">Close</button>
                            </div>
                        ) : details ? (
                            <div className="flex flex-col pb-8">
                                {/* Hero Backdrop */}
                                <div className="relative w-full h-64 sm:h-80 md:h-96">
                                    <AnimatePresence>
                                        {showTrailer && details.trailerUrl ? (
                                            <motion.div
                                                initial={{ opacity: 0 }}
                                                animate={{ opacity: 1 }}
                                                exit={{ opacity: 0 }}
                                                className="absolute inset-0 z-20 bg-black"
                                            >
                                                <iframe
                                                    src={`${details.trailerUrl}?autoplay=1`}
                                                    className="w-full h-full border-0"
                                                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                                                    allowFullScreen
                                                />
                                                <button
                                                    onClick={() => setShowTrailer(false)}
                                                    className="absolute top-4 right-4 z-30 p-2 bg-black/50 hover:bg-black/80 text-white rounded-full backdrop-blur-md transition-colors"
                                                >
                                                    <X className="w-5 h-5" />
                                                </button>
                                            </motion.div>
                                        ) : (
                                            <>
                                                <Image
                                                    src={details.backdropUrl || details.posterUrl}
                                                    alt={details.title}
                                                    fill
                                                    className="object-cover"
                                                    priority
                                                />
                                                <div className="absolute inset-0 bg-gradient-to-t from-dark-800 via-dark-800/80 to-transparent" />

                                                {/* Play Trailer Floating Button */}
                                                {details.trailerUrl && (
                                                    <button
                                                        onClick={() => setShowTrailer(true)}
                                                        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-16 h-16 bg-neon-cyan/80 hover:bg-neon-cyan text-black rounded-full flex items-center justify-center backdrop-blur-md transition-all duration-300 hover:scale-110 shadow-glow-cyan animate-pulse group"
                                                    >
                                                        <Play className="w-8 h-8 ml-1 transition-transform group-hover:scale-110" />
                                                    </button>
                                                )}
                                            </>
                                        )}
                                    </AnimatePresence>
                                </div>

                                {/* Content Details */}
                                <div className="px-6 sm:px-10 -mt-20 relative z-10">
                                    <div className="flex flex-col md:flex-row gap-6 md:gap-10">
                                        {/* Poster (Desktop) */}
                                        <div className="hidden md:block shrink-0 w-48 h-72 relative rounded-xl overflow-hidden shadow-2xl border border-white/10">
                                            <Image src={details.posterUrl} alt={details.title} fill className="object-cover" />
                                        </div>

                                        {/* Info */}
                                        <div className="flex-1 space-y-4">
                                            <h2 className="text-3xl sm:text-4xl font-bold text-white leading-tight">
                                                {details.title}
                                            </h2>

                                            <div className="flex flex-wrap items-center gap-4 text-sm text-gray-300">
                                                <span className="flex items-center gap-1.5 bg-green-500/20 text-green-400 px-3 py-1 rounded-full font-medium">
                                                    <Star className="w-4 h-4 fill-current" />
                                                    {details.rating.toFixed(1)}
                                                </span>
                                                <span className="flex items-center gap-1.5">
                                                    <Calendar className="w-4 h-4" />
                                                    {details.year}
                                                </span>
                                                {details.type === 'movie' && (
                                                    <span className="flex items-center gap-1.5">
                                                        <Clock className="w-4 h-4" />
                                                        {details.duration} min
                                                    </span>
                                                )}
                                                {details.type === 'anime' && (
                                                    <span className="flex items-center gap-1.5">
                                                        <Film className="w-4 h-4" />
                                                        {details.episodes} Episodes
                                                    </span>
                                                )}
                                            </div>

                                            <div className="flex flex-wrap gap-2">
                                                {details.genres.map(g => (
                                                    <span key={g} className="text-xs px-2 py-1 bg-white/10 rounded-md text-gray-300">
                                                        {g}
                                                    </span>
                                                ))}
                                                {details.mood?.map(m => (
                                                    <span key={m} className="text-xs px-2 py-1 bg-neon-purple/20 text-neon-purple rounded-md shadow-glow-purple">
                                                        {m}
                                                    </span>
                                                ))}
                                            </div>

                                            <p className="text-gray-300 leading-relaxed max-w-3xl mt-4">
                                                {details.overview}
                                            </p>

                                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-6 pt-6 border-t border-white/10">
                                                {details.type === 'movie' && details.director && (
                                                    <div>
                                                        <span className="text-gray-500 text-sm block mb-1">Director</span>
                                                        <span className="text-white font-medium">{details.director}</span>
                                                    </div>
                                                )}
                                                {details.type === 'movie' && details.cast && details.cast.length > 0 && (
                                                    <div>
                                                        <span className="text-gray-500 text-sm block mb-1">Top Cast</span>
                                                        <span className="text-white font-medium">{details.cast.slice(0, 3).join(', ')}</span>
                                                    </div>
                                                )}
                                                {details.type === 'anime' && details.studio && (
                                                    <div>
                                                        <span className="text-gray-500 text-sm block mb-1">Studio</span>
                                                        <span className="text-white font-medium">{details.studio}</span>
                                                    </div>
                                                )}
                                                {details.type === 'anime' && details.characters && details.characters.length > 0 && (
                                                    <div>
                                                        <span className="text-gray-500 text-sm block mb-1">Characters</span>
                                                        <span className="text-white font-medium">{details.characters.slice(0, 3).join(', ')}</span>
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                {/* Similar Content Section */}
                                {similar && similar.length > 0 && (
                                    <div className="px-6 sm:px-10 mt-12 bg-dark-900/50 py-8 border-t border-white/5">
                                        <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                                            <SparklesIcon /> Similar Content
                                        </h3>
                                        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
                                            {similar.map((item, idx) => (
                                                <ContentCard key={item.id} content={item} index={idx} />
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </div>
                        ) : null}
                    </motion.div>
                </div>
            )}
        </AnimatePresence>
    );
}

function SparklesIcon() {
    return (
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-neon-cyan">
            <path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z" />
            <path d="M5 3v4" />
            <path d="M19 17v4" />
            <path d="M3 5h4" />
            <path d="M17 19h4" />
        </svg>
    );
}
