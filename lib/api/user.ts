/**
 * User session management for personalization.
 * Handles session creation, persistence, and interaction tracking.
 */

import apiClient from './client';
import { isAxiosError } from 'axios';
import { SessionResponse, TasteProfile } from '@/types/user';

const SESSION_STORAGE_KEY = 'mavilon_session_id';

// Share concurrent initialization (the profile loads several resources at once).
let sessionRequest: Promise<string> | null = null;

async function resolveSession(): Promise<string> {
    const storedId = localStorage.getItem(SESSION_STORAGE_KEY);
    if (storedId) {
        try {
            const response = await apiClient.post<SessionResponse>('/api/users/session', { session_id: storedId });
            localStorage.setItem(SESSION_STORAGE_KEY, response.data.session_id);
            return response.data.session_id;
        } catch (error) {
            // Only a definitive invalid/unknown identity permits replacement.
            // Network/server failures must preserve the user's existing identity.
            if (!isAxiosError(error) || ![404, 422].includes(error.response?.status ?? 0)) {
                throw error;
            }
            localStorage.removeItem(SESSION_STORAGE_KEY);
        }
    }

    const response = await apiClient.post<SessionResponse>('/api/users/session');
    localStorage.setItem(SESSION_STORAGE_KEY, response.data.session_id);
    return response.data.session_id;
}

/** Get a server-confirmed session; never persist a fabricated fallback ID. */
export function getOrCreateSession(): Promise<string> {
    if (!sessionRequest) {
        sessionRequest = resolveSession()
            .catch(() => {
                // Axios errors contain request bodies; do not expose them to callers' logs.
                throw new Error('Unable to establish session');
            })
            .finally(() => { sessionRequest = null; });
    }
    return sessionRequest;
}

/**
 * Get current session ID (without creating new one)
 */
export function getCurrentSession(): string | null {
    return localStorage.getItem(SESSION_STORAGE_KEY);
}

/**
 * Track user interaction with content
 */
export async function trackInteraction(
    contentId: string,
    contentType: 'movie' | 'anime',
    interactionType: 'view' | 'click' | 'search',
    mood?: string
): Promise<void> {
    try {
        const sessionId = await getOrCreateSession();

        await apiClient.post(`/api/users/${sessionId}/interact`, {
            content_id: contentId,
            content_type: contentType,
            interaction_type: interactionType,
            mood: mood
        });
    } catch (error) {
        console.error('Failed to track interaction:', error);
        // Don't throw - interaction tracking should not break the app
    }
}

/**
 * Get user taste profile
 */
export async function getUserProfile(): Promise<TasteProfile> {
    const sessionId = await getOrCreateSession();
    try {
        const response = await apiClient.get<TasteProfile>(`/api/users/${sessionId}/profile`);
        return response.data;
    } catch {
        throw new Error('Unable to load taste profile');
    }
}

/**
 * Add content to user favorites
 */
export async function addToFavorites(contentId: string, contentType: 'movie' | 'anime') {
    const sessionId = await getOrCreateSession();
    const response = await apiClient.post(`/api/users/${sessionId}/favorite`, {
        content_id: contentId,
        content_type: contentType
    });
    return response.data;
}

/**
 * Remove content from user favorites
 */
export async function removeFromFavorites(contentId: string) {
    const sessionId = await getOrCreateSession();
    const response = await apiClient.delete(`/api/users/${sessionId}/favorite/${contentId}`);
    return response.data;
}

/**
 * Get user's favored content IDs 
 */
export async function getFavorites() {
    const sessionId = await getOrCreateSession();
    const response = await apiClient.get(`/api/users/${sessionId}/favorites`);
    return response.data;
}

/**
 * Get user's watch history
 */
export async function getWatchHistory() {
    const sessionId = await getOrCreateSession();
    const response = await apiClient.get(`/api/users/${sessionId}/history`);
    return response.data;
}

/**
 * Remove content from history to reset taste embedding for it
 */
export async function removeFromHistory(contentId: string) {
    const sessionId = await getOrCreateSession();
    const response = await apiClient.delete(`/api/users/${sessionId}/history/${contentId}`);
    return response.data;
}
