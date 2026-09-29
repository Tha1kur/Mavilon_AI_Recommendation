import type { Config } from "tailwindcss";

const config: Config = {
    content: [
        "./pages/**/*.{js,ts,jsx,tsx,mdx}",
        "./components/**/*.{js,ts,jsx,tsx,mdx}",
        "./app/**/*.{js,ts,jsx,tsx,mdx}",
    ],
    theme: {
        extend: {
            colors: {
                // Dark cinematic base
                'dark': {
                    900: '#0a0a0f',
                    800: '#12121a',
                    700: '#1a1a2e',
                    600: '#16213e',
                },
                // Neon accents
                'neon': {
                    cyan: '#00f5ff',
                    purple: '#b24bf3',
                    pink: '#ff006e',
                    blue: '#4361ee',
                },
            },
            backgroundImage: {
                'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
                'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
                'gradient-cinematic': 'linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 50%, #16213e 100%)',
                'gradient-neon': 'linear-gradient(135deg, #00f5ff 0%, #b24bf3 50%, #ff006e 100%)',
            },
            boxShadow: {
                'glow-cyan': '0 0 20px rgba(0, 245, 255, 0.5), 0 0 40px rgba(0, 245, 255, 0.3)',
                'glow-purple': '0 0 20px rgba(178, 75, 243, 0.5), 0 0 40px rgba(178, 75, 243, 0.3)',
                'glow-pink': '0 0 20px rgba(255, 0, 110, 0.5), 0 0 40px rgba(255, 0, 110, 0.3)',
                'glass': '0 8px 32px 0 rgba(0, 245, 255, 0.1)',
            },
            animation: {
                'float': 'float 6s ease-in-out infinite',
                'glow': 'glow 2s ease-in-out infinite alternate',
                'slide-up': 'slideUp 0.5s ease-out',
                'fade-in': 'fadeIn 0.6s ease-out',
            },
            keyframes: {
                float: {
                    '0%, 100%': { transform: 'translateY(0px)' },
                    '50%': { transform: 'translateY(-20px)' },
                },
                glow: {
                    '0%': { boxShadow: '0 0 20px rgba(0, 245, 255, 0.5)' },
                    '100%': { boxShadow: '0 0 40px rgba(178, 75, 243, 0.8)' },
                },
                slideUp: {
                    '0%': { transform: 'translateY(100px)', opacity: '0' },
                    '100%': { transform: 'translateY(0)', opacity: '1' },
                },
                fadeIn: {
                    '0%': { opacity: '0' },
                    '100%': { opacity: '1' },
                },
            },
            backdropBlur: {
                xs: '2px',
            },
        },
    },
    plugins: [],
};

export default config;
