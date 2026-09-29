'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Mood } from '@/types/content';
import { useApp } from '@/lib/context/app-context';

const moods: { name: Mood; emoji: string; color: string }[] = [
    { name: 'Dark', emoji: '🌑', color: 'from-gray-900 to-black' },
    { name: 'Emotional', emoji: '💔', color: 'from-pink-600 to-rose-600' },
    { name: 'Thriller', emoji: '😱', color: 'from-red-600 to-orange-600' },
    { name: 'Romance', emoji: '💕', color: 'from-pink-500 to-purple-500' },
    { name: 'Sci-Fi', emoji: '🚀', color: 'from-blue-600 to-cyan-500' },
    { name: 'Action', emoji: '💥', color: 'from-orange-600 to-red-600' },
    { name: 'Comedy', emoji: '😂', color: 'from-yellow-500 to-orange-500' },
];

export default function MoodSelector() {
    const { selectedMood, setSelectedMood } = useApp();

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="w-full max-w-4xl mx-auto"
        >
            <h3 className="text-center text-lg text-gray-300 mb-4">
                How are you feeling?
            </h3>

            <div className="flex flex-wrap justify-center gap-3">
                {moods.map((mood, index) => {
                    const isSelected = selectedMood === mood.name;

                    return (
                        <motion.button
                            key={mood.name}
                            initial={{ opacity: 0, scale: 0.8 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ duration: 0.3, delay: index * 0.05 }}
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            onClick={() => setSelectedMood(isSelected ? null : mood.name)}
                            className={`
                relative px-6 py-3 rounded-full font-medium
                transition-all duration-300
                ${isSelected
                                    ? 'glass-strong text-white shadow-glow-cyan'
                                    : 'glass text-gray-300 hover:text-white'
                                }
              `}
                        >
                            {/* Background gradient on selected */}
                            {isSelected && (
                                <motion.div
                                    layoutId="mood-bg"
                                    className={`absolute inset-0 bg-gradient-to-r ${mood.color} opacity-20 rounded-full`}
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 0.2 }}
                                    exit={{ opacity: 0 }}
                                />
                            )}

                            <span className="relative z-10 flex items-center gap-2">
                                <span className="text-xl">{mood.emoji}</span>
                                <span>{mood.name}</span>
                            </span>

                            {/* Glow effect on selected */}
                            {isSelected && (
                                <div className="absolute inset-0 rounded-full blur-xl bg-neon-cyan/30 -z-10" />
                            )}
                        </motion.button>
                    );
                })}
            </div>
        </motion.div>
    );
}
