export interface SessionResponse {
    session_id: string;
    user_id: string;
    is_new: boolean;
}

export interface TasteProfile {
    favorite_genres: Record<string, number>;
    favorite_moods: Record<string, number>;
    interaction_count: number;
}
