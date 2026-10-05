/**
 * API client for MAVILON AI backend.
 * Provides type-safe methods for all backend endpoints.
 */

import axios from 'axios';
import { Content, Movie, Anime } from '@/types/content';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create axios instance with default config
const apiClient = axios.create({
    baseURL: API_BASE_URL,
    timeout: 30000, // 30 seconds
    headers: {
        'Content-Type': 'application/json',
    },
});

// Response interceptor for error handling and retries
apiClient.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        // Retry configuration
        const MAX_RETRIES = 3;
        const RETRY_DELAY = 1000; // Start with 1s

        // Check if we should retry (Network Error or 503 Service Unavailable)
        if (
            error.code === 'ERR_NETWORK' ||
            error.message === 'Network Error' ||
            (error.response && error.response.status === 503)
        ) {
            // Initialize retry count
            originalRequest._retryCount = originalRequest._retryCount || 0;

            if (originalRequest._retryCount < MAX_RETRIES) {
                originalRequest._retryCount++;

                // Exponential backoff: 1s, 2s, 4s
                const delay = RETRY_DELAY * Math.pow(2, originalRequest._retryCount - 1);

                console.log(`API Connection failed. Retrying in ${delay}ms... (Attempt ${originalRequest._retryCount}/${MAX_RETRIES})`);

                // Wait for delay
                await new Promise(resolve => setTimeout(resolve, delay));

                // Retry request
                return apiClient(originalRequest);
            }
        }

        // Session validation responses can contain submitted identity values.
        console.error('API Error:', originalRequest?.url === '/api/users/session'
            ? 'Session request failed'
            : error.response?.data || error.message);
        throw error;
    }
);

export default apiClient;
