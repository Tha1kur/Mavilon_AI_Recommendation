'use client';

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { User, Heart, Clock, Activity, Trash2, ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import {
    getUserProfile,
    getFavorites,
    getWatchHistory,
    removeFromHistory,
    removeFromFavorites
} from '@/lib/api/user';
import { getContentDetails } from '@/lib/api/endpoints';
import { Content } from '@/types/content';
import ContentCard from '@/components/ui/ContentCard';

interface ProfileData {
    interaction_count: number;
    favorite_genres?: Record<string, number>;
    favorite_moods?: Record<string, number>;
}

export default function ProfilePage() {
    const [activeTab, setActiveTab] = useState<'taste' | 'favorites' | 'history'>('taste');

    const [profile, setProfile] = useState<ProfileData | null>(null);
    const [favorites, setFavorites] = useState<{ id: string, type: 'movie' | 'anime', content?: Content }[]>([]);
    const [history, setHistory] = useState<{ id: string, type: 'movie' | 'anime', watched_at: string, content?: Content }[]>([]);

    const [loading, setLoading] = useState(true);

    const loadData = async () => {
        setLoading(true);
        try {
            // Fetch baseline data
            const [profileData, favData, histData] = await Promise.all([
                getUserProfile(),
                getFavorites(),
                getWatchHistory()
            ]);

            setProfile(profileData);

            // Re-map backend formats
            const favItems = favData.map((f: any) => ({ id: f.content_id, type: f.content_type }));
            const histItems = histData.map((h: any) => ({ id: h.content_id, type: h.content_type, watched_at: h.watched_at }));

            setFavorites(favItems);
            setHistory(histItems);

            // Enrich with full content parallel fetches
            const enrichItems = async (items: any[]) => {
                const results = await Promise.allSettled(
                    items.map(item => getContentDetails(item.type, item.id))
                );
                return items.map((item, idx) => {
                    const res = results[idx];
                    if (res.status === 'fulfilled') {
                        return { ...item, content: res.value };
                    }
                    return item;
                });
            };

            // Fetch concurrently but separately to not block UI entirely
            enrichItems(favItems).then(setFavorites);
            enrichItems(histItems).then(setHistory);

        } catch (error) {
            console.error("Failed to load profile data:", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadData();
    }, []);

    const handleRemoveHistory = async (id: string) => {
        try {
            // Optimistic update
            setHistory(prev => prev.filter(h => h.id !== id));
            await removeFromHistory(id);
            // Re-fetch profile data implicitly because taste evolved
            const newProfile = await getUserProfile();
            setProfile(newProfile);
        } catch (error) {
            console.error('Failed to remove from history', error);
            // Could add toast here
        }
    };

    const handleRemoveFavorite = async (id: string) => {
        try {
            setFavorites(prev => prev.filter(f => f.id !== id));
            await removeFromFavorites(id);
        } catch (error) {
            console.error('Failed to remove from favorites', error);
        }
    };

    return (
        <main className="min-h-screen py-24 px-6">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="flex items-center gap-4 mb-12">
                    <Link href="/" className="p-3 bg-white/5 rounded-full hover:bg-white/10 transition-colors mr-4">
                        <ArrowLeft className="w-6 h-6 text-white" />
                    </Link>
                    <div className="w-16 h-16 bg-gradient-to-tr from-neon-cyan to-neon-purple rounded-full flex items-center justify-center shadow-glow-cyan">
                        <User className="w-8 h-8 text-white" />
                    </div>
                    <div>
                        <h1 className="text-3xl font-bold text-white">Your AI Profile</h1>
                        <p className="text-gray-400">Discover how MAVILON understands your cinematic taste</p>
                    </div>
                </div>

                {/* Tabs */}
                <div className="flex gap-4 mb-8">
                    {[
                        { id: 'taste', icon: Activity, label: 'Taste Matrix' },
                        { id: 'favorites', icon: Heart, label: 'Favorites' },
                        { id: 'history', icon: Clock, label: 'Watch History' }
                    ].map(tab => (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id as any)}
                            className={`
                                flex items-center gap-2 px-6 py-3 rounded-lg font-medium transition-all duration-300
                                ${activeTab === tab.id
                                    ? 'bg-neon-cyan/20 text-neon-cyan border border-neon-cyan/50 shadow-glow-cyan'
                                    : 'bg-white/5 text-gray-400 border border-transparent hover:bg-white/10 hover:text-white'
                                }
                            `}
                        >
                            <tab.icon className="w-5 h-5" />
                            {tab.label}
                        </button>
                    ))}
                </div>

                {/* Content Area */}
                {loading ? (
                    <div className="h-64 flex items-center justify-center">
                        <div className="w-12 h-12 border-4 border-neon-cyan border-t-transparent rounded-full animate-spin"></div>
                    </div>
                ) : (
                    <motion.div
                        key={activeTab}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        className="min-h-[500px]"
                    >
                        {/* Taste Matrix */}
                        {activeTab === 'taste' && profile && (
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                                <div className="glass-strong p-8 rounded-2xl">
                                    <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                                        <Activity className="w-5 h-5 text-neon-cyan" /> Network Analytics
                                    </h3>
                                    <div className="space-y-6">
                                        <div>
                                            <p className="text-gray-400 text-sm">Semantic Interactions</p>
                                            <p className="text-4xl font-bold text-white font-mono mt-1">{profile.interaction_count}</p>
                                        </div>
                                        <div className="pt-6 border-t border-white/10">
                                            <p className="text-sm text-gray-400 mb-4">Top Genres Recognized</p>
                                            <div className="flex flex-wrap gap-2">
                                                {profile.favorite_genres && Object.entries(profile.favorite_genres).length > 0
                                                    ? Object.entries(profile.favorite_genres)
                                                        .sort(([, a], [, b]) => b - a)
                                                        .slice(0, 8)
                                                        .map(([genre, score]) => (
                                                            <span key={genre} className="bg-white/10 px-3 py-1.5 rounded-lg text-sm text-white">
                                                                {genre} <span className="opacity-50 text-xs ml-1">{Math.round(score)}</span>
                                                            </span>
                                                        ))
                                                    : <span className="text-gray-500 italic">Not enough data to determine preferred genres.</span>
                                                }
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div className="glass-strong p-8 rounded-2xl">
                                    <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                                        <Heart className="w-5 h-5 text-neon-purple" /> Mood Affinity
                                    </h3>
                                    <div className="space-y-6">
                                        <p className="text-sm text-gray-400 mb-2">Based on your recent history, MAVILON identifies these emotional resonances:</p>
                                        <div className="flex flex-col gap-3">
                                            {profile.favorite_moods && Object.entries(profile.favorite_moods).length > 0
                                                ? Object.entries(profile.favorite_moods)
                                                    .sort(([, a], [, b]) => b - a)
                                                    .map(([mood, score], idx) => {
                                                        const maxScore = Math.max(...Object.values(profile.favorite_moods!));
                                                        const width = `${(score / maxScore) * 100}%`;
                                                        return (
                                                            <div key={mood} className="space-y-1">
                                                                <div className="flex justify-between text-sm">
                                                                    <span className="text-white">{mood}</span>
                                                                    <span className="text-gray-400">{Math.round(score * 10) / 10}</span>
                                                                </div>
                                                                <div className="h-2 w-full bg-dark-900 rounded-full overflow-hidden">
                                                                    <div
                                                                        className="h-full bg-gradient-to-r from-neon-purple to-neon-pink rounded-full"
                                                                        style={{ width }}
                                                                    />
                                                                </div>
                                                            </div>
                                                        )
                                                    })
                                                : <span className="text-gray-500 italic">Play a few trailers to establish your mood affinities!</span>
                                            }
                                        </div>
                                        <p className="text-xs text-gray-500 mt-4 border-t border-white/5 pt-4">Your taste profile is constantly evolving using an Exponential Moving Average algorithm across your interactions.</p>
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Favorites */}
                        {activeTab === 'favorites' && (
                            <div>
                                {favorites.length === 0 ? (
                                    <div className="glass-strong p-12 rounded-2xl text-center">
                                        <Heart className="w-12 h-12 text-gray-500 mx-auto mb-4" />
                                        <h3 className="text-xl font-bold text-white mb-2">No favorites yet</h3>
                                        <p className="text-gray-400 max-w-sm mx-auto">Click the + icon on any movie or anime to add it to your collection.</p>
                                    </div>
                                ) : (
                                    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6">
                                        {favorites.map((fav) => (
                                            <div key={fav.id} className="relative group">
                                                {fav.content ? (
                                                    <ContentCard content={fav.content} />
                                                ) : (
                                                    <div className="aspect-[2/3] w-full bg-white/5 rounded-xl animate-pulse" />
                                                )}
                                                {/* Remove from Favorites Overlay Action */}
                                                <button
                                                    onClick={() => handleRemoveFavorite(fav.id)}
                                                    className="absolute -top-2 -right-2 z-10 p-2 bg-red-500/80 hover:bg-red-500 text-white rounded-full shadow-lg opacity-0 transition-opacity group-hover:opacity-100 backdrop-blur-md"
                                                    title="Remove from favorites"
                                                >
                                                    <Trash2 className="w-4 h-4" />
                                                </button>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        )}

                        {/* Watch History */}
                        {activeTab === 'history' && (
                            <div>
                                <p className="text-sm text-gray-400 mb-6 flex items-center gap-2">
                                    <span className="block w-2 h-2 rounded-full bg-neon-cyan animate-pulse" />
                                    Items here actively influence the AI that is recommending your content. Remove items to correct its course.
                                </p>
                                {history.length === 0 ? (
                                    <div className="glass-strong p-12 rounded-2xl text-center">
                                        <Clock className="w-12 h-12 text-gray-500 mx-auto mb-4" />
                                        <h3 className="text-xl font-bold text-white mb-2">Your history is empty</h3>
                                        <p className="text-gray-400 max-w-sm mx-auto">Interact with content to start building your history.</p>
                                    </div>
                                ) : (
                                    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6">
                                        {history.map((hist) => (
                                            <div key={hist.id} className="relative group">
                                                {hist.content ? (
                                                    <ContentCard content={hist.content} />
                                                ) : (
                                                    <div className="aspect-[2/3] w-full bg-white/5 rounded-xl animate-pulse" />
                                                )}
                                                {/* Remove from History Overlay Action */}
                                                <button
                                                    onClick={() => handleRemoveHistory(hist.id)}
                                                    className="absolute -top-2 -right-2 z-10 p-2 bg-red-500/80 hover:bg-red-500 text-white rounded-full shadow-lg opacity-0 transition-opacity group-hover:opacity-100 backdrop-blur-md"
                                                    title="Remove from history (Recalibrate AI)"
                                                >
                                                    <Trash2 className="w-4 h-4" />
                                                </button>
                                                <div className="absolute bottom-2 left-2 z-10 bg-black/80 px-2 py-1 rounded text-[10px] text-gray-300 backdrop-blur-md border border-white/10 opacity-0 group-hover:opacity-100 transition-opacity">
                                                    {new Date(hist.watched_at).toLocaleDateString()}
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        )}
                    </motion.div>
                )}
            </div>
        </main>
    );
}
