'use client';

import { motion } from 'framer-motion';

export default function Logo({ size = 'large' }: { size?: 'small' | 'medium' | 'large' }) {
    const sizes = {
        small: { text: 'text-2xl', container: 'h-12' },
        medium: { text: 'text-4xl', container: 'h-16' },
        large: { text: 'text-6xl md:text-7xl', container: 'h-20 md:h-24' },
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className={`${sizes[size].container} flex items-center justify-center`}
        >
            <div className="relative">
                {/* Glow effect */}
                <div className="absolute inset-0 blur-2xl bg-gradient-neon opacity-50 animate-glow" />

                {/* Logo text */}
                <h1 className={`${sizes[size].text} font-bold tracking-wider relative z-10`}>
                    <span className="text-gradient">MAVILON</span>
                    <span className="text-neon-cyan ml-2">AI</span>
                </h1>
            </div>
        </motion.div>
    );
}
