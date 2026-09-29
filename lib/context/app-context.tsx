'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { Content, Mood, ContentType } from '@/types/content';
import { searchContent } from '@/lib/api/endpoints';

interface AppContextType {
    // State
    searchQuery: string;
    selectedMood: Mood | null;
    selectedContentType: ContentType;
    activeSection: 'trending' | 'search' | 'recommendations';
    searchResults: Content[];
    isSearching: boolean;
    searchError: string | null;

    // Actions
    setSearchQuery: (query: string) => void;
    setSelectedMood: (mood: Mood | null) => void;
    setSelectedContentType: (type: ContentType) => void;
    performSearch: (query: string, mood?: Mood) => Promise<void>;
    clearSearch: () => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export function AppContextProvider({ children }: { children: React.ReactNode }) {
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedMood, setSelectedMood] = useState<Mood | null>(null);
    const [selectedContentType, setSelectedContentType] = useState<ContentType>('movie');
    const [activeSection, setActiveSection] = useState<'trending' | 'search' | 'recommendations'>('trending');
    const [searchResults, setSearchResults] = useState<Content[]>([]);
    const [isSearching, setIsSearching] = useState(false);
    const [searchError, setSearchError] = useState<string | null>(null);

    const performSearch = async (query: string, mood?: Mood) => {
        if (!query.trim()) return;

        setIsSearching(true);
        setSearchError(null);
        setActiveSection('search');

        try {
            // Include mood in search if selected
            const effectiveMood = mood || (selectedMood ? (selectedMood as string) : undefined);

            // Call API
            const results = await searchContent(query, effectiveMood);
            setSearchResults(results);
        } catch (error) {
            console.error('Search failed:', error);
            setSearchError('Failed to search content. Please try again.');
            setSearchResults([]);
        } finally {
            setIsSearching(false);
        }
    };

    const clearSearch = () => {
        setSearchQuery('');
        setSearchResults([]);
        setActiveSection('trending');
        setSearchError(null);
    };

    // Effect: Update active section based on interactions
    useEffect(() => {
        if (selectedMood && activeSection !== 'search') {
            // If user clicks a mood, we might want to scroll to recommendations or just update them
            // For now, let's keep 'trending' as default unless they search
        }
    }, [selectedMood, activeSection]);

    const value = {
        searchQuery,
        selectedMood,
        selectedContentType,
        activeSection,
        searchResults,
        isSearching,
        searchError,
        setSearchQuery,
        setSelectedMood,
        setSelectedContentType,
        performSearch,
        clearSearch
    };

    return (
        <AppContext.Provider value={value}>
            {children}
        </AppContext.Provider>
    );
}

export function useApp() {
    const context = useContext(AppContext);
    if (context === undefined) {
        throw new Error('useApp must be used within an AppContextProvider');
    }
    return context;
}
