'use client';

import dynamic from 'next/dynamic';

const ParticleField = dynamic(() => import('./ParticleField'), {
    ssr: false,
});

export default function CinematicBackground() {
    return (
        <div className="fixed inset-0 -z-10 overflow-hidden">
            {/* Base gradient */}
            <div className="absolute inset-0 bg-gradient-cinematic" />

            {/* Animated gradient overlay */}
            <div className="absolute inset-0 bg-gradient-to-br from-dark-900 via-dark-700/50 to-dark-900 animate-pulse"
                style={{ animationDuration: '8s' }} />

            {/* Light streaks */}
            <div className="absolute top-0 left-1/4 w-1 h-full bg-gradient-to-b from-transparent via-neon-cyan/20 to-transparent blur-sm" />
            <div className="absolute top-0 right-1/3 w-1 h-full bg-gradient-to-b from-transparent via-neon-purple/20 to-transparent blur-sm" />
            <div className="absolute top-0 right-1/4 w-1 h-full bg-gradient-to-b from-transparent via-neon-pink/20 to-transparent blur-sm" />

            {/* Fog effect */}
            <div className="absolute inset-0 bg-gradient-radial from-transparent via-dark-800/30 to-dark-900/80" />

            {/* Particle field */}
            <ParticleField />

            {/* Vignette */}
            <div className="absolute inset-0 bg-gradient-radial from-transparent via-transparent to-dark-900" />
        </div>
    );
}
