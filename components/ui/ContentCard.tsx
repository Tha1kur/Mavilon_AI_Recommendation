'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Star, Play, Plus, Info, Check, Sparkles } from 'lucide-react';
import Image from 'next/image';
import { Content } from '@/types/content';
import { trackInteraction, addToFavorites, removeFromFavorites } from '@/lib/api/user';
import ContentDetailsModal from './ContentDetailsModal';

interface ContentCardProps {
    content: Content;
    index?: number;
    explanation?: string; // AI explanation for recommendation
}

export default function ContentCard({ content, index = 0, explanation }: ContentCardProps) {
    const [isHovered, setIsHovered] = useState(false);
    const [isFavorited, setIsFavorited] = useState(false);
    const [isModalOpen, setIsModalOpen] = useState(false);

    const handleFavorite = async (e: React.MouseEvent) => {
        e.stopPropagation();
        try {
            if (isFavorited) {
                setIsFavorited(false); // Optimistic UI
                await removeFromFavorites(content.id);
            } else {
                setIsFavorited(true); // Optimistic UI
                await addToFavorites(content.id, content.type);
            }
        } catch (err) {
            // Revert on error
            setIsFavorited(!isFavorited);
            console.error('Failed to toggle favorite:', err);
        }
    };

    const handleOpenModal = (e: React.MouseEvent) => {
        e.stopPropagation();
        setIsModalOpen(true);
        trackInteraction(content.id, content.type, 'view');
    };

    return (
        <>
            <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                className="group relative aspect-[2/3] w-full overflow-hidden rounded-xl bg-dark-800 border border-white/5 cursor-pointer transition-all duration-300 hover:scale-[1.03] hover:border-white/20 hover:shadow-glow-cyan"
                onClick={handleOpenModal}
            >
                <Image
                    src={content.posterUrl || 'https://images.unsplash.com/photo-1598899134739-24c46f58b8c0?w=800&q=80'}
                    alt={content.title}
                    fill
                    className="object-cover transition-transform duration-700 group-hover:scale-110"
                />

                {/* Top-Right Neon Rating */}
                <div className="absolute top-2 right-2 z-10 bg-black/40 backdrop-blur-md px-2 py-1 rounded-md border border-white/10 flex items-center gap-1 shadow-glow-cyan">
                    <Star className="w-3 h-3 text-neon-cyan fill-current" />
                    <span className="text-xs font-bold text-white tracking-wide">{content.rating.toFixed(1)}</span>
                </div>

                {/* Gradient Overlay */}
                <div className="absolute inset-0 bg-gradient-to-t from-black via-black/50 to-transparent opacity-80" />

                {/* Small Center Play Button on Hover */}
                <div className="absolute inset-0 flex items-center justify-center opacity-0 transition-opacity duration-300 group-hover:opacity-100 z-10">
                    <button
                        className="w-12 h-12 bg-white/20 backdrop-blur-md border border-white/30 rounded-full flex items-center justify-center text-white hover:bg-white/40 hover:scale-110 transition-all shadow-glow-cyan"
                        onClick={(e) => {
                            e.stopPropagation();
                            if (content.trailerUrl) {
                                window.open(content.trailerUrl, '_blank');
                                trackInteraction(content.id, content.type, 'click');
                            } else {
                                handleOpenModal(e);
                            }
                        }}
                    >
                        <Play className="w-5 h-5 ml-1 fill-current" />
                    </button>
                </div>

                {/* Bottom Content */}
                <div className="absolute bottom-0 left-0 right-0 p-4 translate-y-2 opacity-0 transition-all duration-300 group-hover:translate-y-0 group-hover:opacity-100 flex flex-col gap-2 z-20">
                    <h3 className="text-lg font-bold text-transparent bg-clip-text bg-gradient-to-r from-white to-white/70 line-clamp-1">{content.title}</h3>

                    <div className="flex items-center gap-2 text-xs text-zinc-400 font-medium">
                        <span className="bg-white/10 backdrop-blur-md px-2 py-0.5 rounded border border-white/5">{content.type.toUpperCase()}</span>
                        <span>{content.year}</span>
                    </div>

                    <div className="flex items-center gap-2 mt-2">
                        <button
                            className={`flex-1 py-1.5 rounded-lg backdrop-blur-md border transition-colors flex items-center justify-center gap-1 text-xs font-semibold ${isFavorited ? 'bg-neon-pink/10 border-neon-pink/30 text-neon-pink shadow-glow-pink' : 'bg-white/10 border-white/10 text-white hover:bg-white/20'}`}
                            onClick={handleFavorite}
                            title={isFavorited ? "Remove from Favorites" : "Add to Favorites"}
                        >
                            {isFavorited ? <Check className="w-3 h-3" /> : <Plus className="w-3 h-3" />}
                            {isFavorited ? "Saved" : "Save"}
                        </button>
                        <button
                            className="flex-1 py-1.5 bg-white/10 border border-white/10 text-white rounded-lg hover:bg-white/20 backdrop-blur-md transition-colors flex items-center justify-center gap-1 text-xs font-semibold"
                            onClick={handleOpenModal}
                            title="View Details"
                        >
                            <Info className="w-3 h-3" />
                            Details
                        </button>
                    </div>

                    {/* AI Explanation Tooltip / Banner */}
                    {explanation && (
                        <div className="mt-1 bg-neon-purple/10 border border-neon-purple/30 p-2 rounded-lg shadow-glow-purple backdrop-blur-md">
                            <p className="text-xs text-purple-200 line-clamp-2 leading-relaxed">
                                <Sparkles className="w-3 h-3 inline mr-1 text-neon-purple" />
                                {explanation}
                            </p>
                        </div>
                    )}
                </div>
            </motion.div>

            <ContentDetailsModal
                contentId={content.id}
                contentType={content.type}
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
            />
        </>
    );
}
