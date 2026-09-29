/**
 * API endpoint functions for frontend.
 * Type-safe wrappers around backend API calls.
 */

import apiClient from './client';
import { Content, Movie, Anime } from '@/types/content';

/**
 * Get trending movies from TMDB
 */
export async function getTrendingMovies(limit: number = 20): Promise<Movie[]> {
    const response = await apiClient.get<Movie[]>('/api/movies/trending', {
        params: { limit },
    });
    return response.data;
}

/**
 * Get trending anime from AniList
 */
export async function getTrendingAnime(limit: number = 20): Promise<Anime[]> {
    const response = await apiClient.get<Anime[]>('/api/anime/trending', {
        params: { limit },
    });
    return response.data;
}

/**
 * Search for content (movies and anime) by query
 */
export async function searchContent(
    query: string,
    mood?: string
): Promise<Content[]> {
    const response = await apiClient.post<Content[]>('/api/search', {
        query,
        mood,
    });
    return response.data;
}

/**
 * Get AI-powered recommendations with personalization
 */
export async function getRecommendations(
    mood?: string,
    limit: number = 6,
    sessionId?: string
): Promise<Array<{
    content: Content;
    explanation: string;
    score: number;
}>> {
    const response = await apiClient.post('/api/recommend', {
        mood,
        limit,
    }, {
        params: sessionId ? { session_id: sessionId } : undefined
    });
    return response.data;
}

/**
 * Check backend health status
 */
export async function checkHealth(): Promise<{
    status: string;
    tmdb_configured: boolean;
    anilist_configured: boolean;
    ai_model: string;
}> {
    const response = await apiClient.get('/health');
    return response.data;
}

/**
 * Get detailed metadata for specific content
 */
export async function getContentDetails(type: 'movie' | 'anime', id: string): Promise<Content> {
    const response = await apiClient.get<Content>(`/api/content/${type}/${id}`);
    return response.data;
}

/**
 * Get similar content matching the target based on AI embeddings
 */
export async function getSimilarContent(type: 'movie' | 'anime', id: string, limit: number = 6): Promise<Content[]> {
    const response = await apiClient.get<Content[]>(`/api/content/${type}/${id}/similar`, {
        params: { limit }
    });
    return response.data;
}

export interface ChatResult {
    content: Content;
    explanation: string;
    score: number;
}

export interface ChatResponse {
    response: string;
    results: ChatResult[];
    detected_mood?: string;
    detected_genres?: string[];
}

/**
 * Send natural language query to the AI chat backend
 */
export async function sendChatMessage(query: string, sessionId?: string, limit: number = 10): Promise<ChatResponse> {
    const response = await apiClient.post<ChatResponse>('/api/chat', {
        query,
        session_id: sessionId,
        limit
    });
    return response.data;
}

