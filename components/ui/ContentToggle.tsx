'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Film, Tv } from 'lucide-react';
import { ContentType } from '@/types/content';
import { useApp } from '@/lib/context/app-context';

export default function ContentToggle() {
    const { selectedContentType, setSelectedContentType } = useApp();

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
            className="flex justify-center"
        >
            <div className="relative glass-strong rounded-full p-1 flex gap-1">
                {/* Sliding background */}
                <motion.div
                    layoutId="toggle-bg"
                    className="absolute top-1 bottom-1 bg-gradient-to-r from-neon-cyan to-neon-purple rounded-full"
                    initial={false}
                    animate={{
                        left: selectedContentType === 'movie' ? '4px' : '50%',
                        right: selectedContentType === 'movie' ? '50%' : '4px',
                    }}
                    transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                />

                {/* Movie button */}
                <button
                    onClick={() => setSelectedContentType('movie')}
                    className={`
            relative z-10 px-8 py-3 rounded-full font-medium
            transition-colors duration-300 flex items-center gap-2
            ${selectedContentType === 'movie' ? 'text-white' : 'text-gray-400'}
          `}
                >
                    <Film className="w-5 h-5" />
                    <span>Movies</span>
                </button>

                {/* Anime button */}
                <button
                    onClick={() => setSelectedContentType('anime')}
                    className={`
            relative z-10 px-8 py-3 rounded-full font-medium
            transition-colors duration-300 flex items-center gap-2
            ${selectedContentType === 'anime' ? 'text-white' : 'text-gray-400'}
          `}
                >
                    <Tv className="w-5 h-5" />
                    <span>Anime</span>
                </button>
            </div>
        </motion.div>
    );
}
