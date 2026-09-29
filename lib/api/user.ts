/**
 * User session management for personalization.
 * Handles session creation, persistence, and interaction tracking.
 */

import apiClient from './client';

const SESSION_STORAGE_KEY = 'mavilon_session_id';

/**
 * Get or create user session
 */
export async function getOrCreateSession(): Promise<string> {
    // Check localStorage for existing session
    let sessionId = localStorage.getItem(SESSION_STORAGE_KEY);

    if (sessionId) {
        // Verify session is still valid
        try {
            await apiClient.post('/api/users/session', { session_id: sessionId });
            return sessionId;
        } catch (error) {
            // Session invalid, create new one
            console.warn('Existing session invalid, creating new one');
            localStorage.removeItem(SESSION_STORAGE_KEY);
            sessionId = null;
        }
    }

    // Create new session
    try {
        const response = await apiClient.post<{ session_id: string; user_id: string; is_new: boolean }>('/api/users/session');
        sessionId = response.data.session_id;

        // Store in localStorage
        localStorage.setItem(SESSION_STORAGE_KEY, sessionId);

        return sessionId;
    } catch (error) {
        console.error('Failed to create session:', error);
        // Generate fallback session ID
        const fallbackId = `fallback_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        localStorage.setItem(SESSION_STORAGE_KEY, fallbackId);
        return fallbackId;
    }
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
export async function getUserProfile(): Promise<{
    favorite_genres?: Record<string, number>;
    favorite_moods?: Record<string, number>;
    interaction_count: number;
}> {
    try {
        const sessionId = await getOrCreateSession();
        const response = await apiClient.get(`/api/users/${sessionId}/profile`);
        return response.data;
    } catch (error) {
        console.error('Failed to get user profile:', error);
        return { interaction_count: 0 };
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
