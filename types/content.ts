export type ContentType = 'movie' | 'anime';

export type Mood =
    | 'Dark'
    | 'Emotional'
    | 'Thriller'
    | 'Romance'
    | 'Sci-Fi'
    | 'Action'
    | 'Comedy'
    | 'Mystery'
    | 'Fantasy';

export type Genre =
    | 'Action'
    | 'Adventure'
    | 'Animation'
    | 'Comedy'
    | 'Crime'
    | 'Documentary'
    | 'Drama'
    | 'Fantasy'
    | 'Horror'
    | 'Mystery'
    | 'Romance'
    | 'Sci-Fi'
    | 'Thriller'
    | 'Psychological'
    | 'Supernatural'
    | 'Slice of Life';

export interface Movie {
    id: string;
    type: 'movie';
    title: string;
    posterUrl: string;
    backdropUrl?: string;
    genres: Genre[];
    rating: number;
    year: number;
    duration: number; // in minutes
    overview: string;
    trailerUrl?: string;
    cast?: string[];
    director?: string;
    mood?: Mood[];
    similar?: Content[];
}

export interface Anime {
    id: string;
    type: 'anime';
    title: string;
    posterUrl: string;
    backdropUrl?: string;
    genres: Genre[];
    rating: number;
    year: number;
    episodes: number;
    overview: string;
    trailerUrl?: string;
    characters?: string[];
    studio?: string;
    mood?: Mood[];
    similar?: Content[];
}

export type Content = Movie | Anime;

export interface RecommendationReason {
    title: string;
    description: string;
    matchScore: number; // 0-100
}

export interface ContentRecommendation {
    content: Content;
    reason: RecommendationReason;
    similarTo?: Content[];
}
