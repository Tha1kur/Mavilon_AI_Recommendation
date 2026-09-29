'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Search, Sparkles, Loader2 } from 'lucide-react';
import { useApp } from '@/lib/context/app-context';

export default function SearchBar() {
    const { performSearch, isSearching } = useApp();
    const [isFocused, setIsFocused] = useState(false);
    const [query, setQuery] = useState('');

    // ... (rest of initial render) ...

    {/* Search Icon */ }
    <button
        onClick={() => performSearch(query)}
        disabled={isSearching}
        className="absolute right-6 top-1/2 -translate-y-1/2 z-10"
    >
        <div className={`
            p-2 rounded-lg transition-all duration-300
            ${isFocused ? 'bg-neon-cyan/20 text-neon-cyan' : 'bg-white/5 text-gray-400'}
          `}>
            {isSearching ? <Loader2 className="w-5 h-5 animate-spin" /> : <Search className="w-5 h-5" />}
        </div>
    </button>

    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="w-full max-w-3xl mx-auto"
        >
            <div className={`
        relative glass-strong rounded-2xl overflow-hidden transition-all duration-300
        ${isFocused ? 'shadow-glow-cyan scale-105' : 'shadow-glass'}
      `}>
                {/* AI Sparkle Icon */}
                <div className="absolute left-6 top-1/2 -translate-y-1/2 z-10">
                    <Sparkles
                        className={`w-6 h-6 transition-colors duration-300 ${isFocused ? 'text-neon-cyan' : 'text-gray-400'
                            }`}
                    />
                </div>

                {/* Search Input */}
                <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onFocus={() => setIsFocused(true)}
                    onBlur={() => setIsFocused(false)}
                    onKeyDown={(e) => {
                        if (e.key === 'Enter') {
                            performSearch(query);
                        }
                    }}
                    placeholder="Ask AI to discover your next story..."
                    disabled={isSearching}
                    className="
            w-full px-16 py-5 bg-transparent text-white text-lg
            placeholder:text-gray-400 outline-none
          "
                />

                {/* Search Icon */}
                <button className="absolute right-6 top-1/2 -translate-y-1/2 z-10">
                    <div className={`
            p-2 rounded-lg transition-all duration-300
            ${isFocused ? 'bg-neon-cyan/20 text-neon-cyan' : 'bg-white/5 text-gray-400'}
          `}>
                        <Search className="w-5 h-5" />
                    </div>
                </button>

                {/* Animated border */}
                {isFocused && (
                    <motion.div
                        layoutId="search-border"
                        className="absolute inset-0 border-2 border-neon-cyan rounded-2xl pointer-events-none"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                    />
                )}
            </div>

            {/* AI hint */}
            <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: isFocused ? 1 : 0.6 }}
                className="text-center text-sm text-gray-400 mt-3"
            >
                Try: &quot;Dark psychological thriller&quot; or &quot;Emotional sci-fi like Interstellar&quot;
            </motion.p>
        </motion.div>
    );
}
