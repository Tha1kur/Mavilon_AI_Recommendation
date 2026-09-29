"""
Taste Reasoning Module for Intelligent Recommendations.
Implements exploration logic, genre adjacency, and taste confidence calculation.
"""

import random
from typing import List, Set, Optional
import numpy as np


# Genre adjacency map for intelligent exploration
GENRE_ADJACENCY = {
    "Sci-Fi": ["Thriller", "Mystery", "Fantasy", "Action"],
    "Thriller": ["Mystery", "Crime", "Horror", "Psychological"],
    "Action": ["Adventure", "Sci-Fi", "Thriller"],
    "Adventure": ["Action", "Fantasy", "Animation"],
    "Romance": ["Drama", "Comedy", "Slice of Life"],
    "Drama": ["Romance", "Psychological", "Mystery"],
    "Comedy": ["Slice of Life", "Romance", "Animation"],
    "Horror": ["Thriller", "Mystery", "Psychological", "Supernatural"],
    "Mystery": ["Thriller", "Crime", "Psychological", "Horror"],
    "Fantasy": ["Sci-Fi", "Adventure", "Supernatural", "Animation"],
    "Crime": ["Thriller", "Mystery", "Drama"],
    "Animation": ["Fantasy", "Adventure", "Comedy", "Slice of Life"],
    "Psychological": ["Thriller", "Horror", "Mystery", "Drama"],
    "Supernatural": ["Horror", "Fantasy", "Mystery"],
    "Slice of Life": ["Comedy", "Drama", "Romance"],
    "Documentary": ["Drama"],
}


class TasteReasoning:
    """Handles taste-based reasoning and exploration logic."""
    
    @staticmethod
    def compute_taste_confidence(interaction_count: int) -> float:
        """
        Compute taste confidence based on interaction history.
        
        Args:
            interaction_count: Number of user interactions
            
        Returns:
            Confidence score from 0.0 (no confidence) to 1.0 (high confidence)
        """
        if interaction_count < 5:
            return 0.0  # Not enough data
        elif interaction_count < 10:
            return 0.3  # Low confidence
        elif interaction_count < 20:
            return 0.6  # Medium confidence
        else:
            return min(1.0, 0.6 + (interaction_count - 20) * 0.02)  # High confidence, caps at 1.0
    
    @staticmethod
    def get_exploration_rate(confidence: float) -> float:
        """
        Determine exploration rate based on taste confidence.
        
        Args:
            confidence: Taste confidence (0.0-1.0)
            
        Returns:
            Exploration rate (0.0-0.15)
        """
        if confidence == 0.0:
            return 0.0  # No exploration for new users
        elif confidence < 0.5:
            return 0.15  # 15% exploration for low confidence
        elif confidence < 0.8:
            return 0.10  # 10% exploration for medium confidence
        else:
            return 0.05  # 5% exploration for high confidence
    
    @staticmethod
    def should_explore(
        confidence: float,
        interaction_count: int,
        random_seed: Optional[float] = None
    ) -> bool:
        """
        Determine if exploration should occur (ε-greedy strategy).
        
        Args:
            confidence: Taste confidence (0.0-1.0)
            interaction_count: Number of user interactions
            random_seed: Optional seed for deterministic testing
            
        Returns:
            True if should explore, False otherwise
        """
        # Disable exploration for new users
        if interaction_count < 5:
            return False
        
        exploration_rate = TasteReasoning.get_exploration_rate(confidence)
        
        # Use seed for deterministic behavior (based on interaction count)
        if random_seed is None:
            random_seed = random.random()
        
        return random_seed < exploration_rate
    
    @staticmethod
    def get_adjacent_genres(favorite_genres: List[str]) -> Set[str]:
        """
        Get genres adjacent to user's favorite genres.
        
        Args:
            favorite_genres: List of user's favorite genres
            
        Returns:
            Set of adjacent genres for exploration
        """
        adjacent = set()
        
        for genre in favorite_genres[:3]:  # Use top 3 favorite genres
            if genre in GENRE_ADJACENCY:
                adjacent.update(GENRE_ADJACENCY[genre])
        
        # Remove genres that are already in favorites
        adjacent -= set(favorite_genres)
        
        return adjacent
    
    @staticmethod
    def compute_exploration_bonus(
        content_genres: List[str],
        favorite_genres: List[str],
        is_exploring: bool
    ) -> float:
        """
        Compute exploration bonus for content.
        
        Args:
            content_genres: Genres of the content
            favorite_genres: User's favorite genres
            is_exploring: Whether we're in exploration mode
            
        Returns:
            Exploration bonus (0.0-1.0)
        """
        if not is_exploring:
            return 0.0
        
        # Get adjacent genres
        adjacent_genres = TasteReasoning.get_adjacent_genres(favorite_genres)
        
        # Check if content has adjacent genres
        content_genre_set = set(content_genres)
        matching_adjacent = content_genre_set & adjacent_genres
        
        if matching_adjacent:
            # Bonus proportional to number of matching adjacent genres
            return min(1.0, len(matching_adjacent) * 0.5)
        
        return 0.0
    
    @staticmethod
    def compute_mood_match_score(
        content_mood: Optional[List[str]],
        selected_mood: Optional[str],
        favorite_moods: Optional[List[str]]
    ) -> float:
        """
        Compute mood match score.
        
        Args:
            content_mood: Moods associated with content
            selected_mood: Currently selected mood filter
            favorite_moods: User's favorite moods
            
        Returns:
            Mood match score (0.0-1.0)
        """
        if not content_mood:
            return 0.0
        
        score = 0.0
        
        # Strong match if content matches selected mood
        if selected_mood and selected_mood in content_mood:
            score += 0.7
        
        # Additional match if content matches favorite moods
        if favorite_moods:
            matching_favorites = set(content_mood) & set(favorite_moods)
            if matching_favorites:
                score += 0.3 * (len(matching_favorites) / len(favorite_moods))
        
        return min(1.0, score)
    
    @staticmethod
    def is_exploration_candidate(
        content_genres: List[str],
        favorite_genres: List[str]
    ) -> bool:
        """
        Check if content is a valid exploration candidate.
        
        Args:
            content_genres: Genres of the content
            favorite_genres: User's favorite genres
            
        Returns:
            True if content has adjacent genres but not favorite genres
        """
        adjacent_genres = TasteReasoning.get_adjacent_genres(favorite_genres)
        content_genre_set = set(content_genres)
        favorite_genre_set = set(favorite_genres)
        
        # Has adjacent genres but not in favorites
        has_adjacent = bool(content_genre_set & adjacent_genres)
        not_in_favorites = not bool(content_genre_set & favorite_genre_set)
        
        return has_adjacent and not_in_favorites

    @staticmethod
    def compute_rating_boost(rating: float) -> float:
        """
        Compute non-linear rating boost.
        - Heavy penalty below 6
        - Neutral band between 6-7
        - Exponential boost above 8
        """
        if rating < 6.0:
            return 0.1 * (rating / 10.0)  # Heavy penalty
        elif rating < 7.0:
            return 0.5 * (rating / 10.0)  # Neutral scaling
        else:
            return (rating / 10.0) ** 2  # Exponential scaling for masterpiece

    @staticmethod
    def compute_popularity_score(popularity: Optional[float], max_expected_log: float = 8.0) -> float:
        """
        Compute log-scaled popularity score to prevent extreme skew.
        """
        if popularity is None or popularity <= 0:
            return 0.0
        
        # Log1p handles small/zero popularities gracefully
        # max_expected_log 8.0 corresponds roughly to popularity ~ 2980
        log_pop = np.log1p(popularity)
        return min(1.0, log_pop / max_expected_log)

    @staticmethod
    def compute_recency_score(release_year: int, current_year: int = 2026, decay_lambda: float = 0.05) -> float:
        """
        Compute recency score using exponential decay.
        """
        if release_year <= 0:
            return 0.0
            
        years_ago = max(0, current_year - release_year)
        
        return np.exp(-decay_lambda * years_ago)

    @staticmethod
    def compute_diversity_penalty(similarity: float, penalty_strength: float = 0.3, similarity_threshold: float = 0.75) -> float:
        """
        Compute a soft diversity penalty instead of hard rejection.
        Only penalizes items that exceed the similarity threshold.
        """
        if similarity <= similarity_threshold:
            return 0.0
            
        penalty = (similarity - similarity_threshold) * penalty_strength
        return min(0.9, penalty)  # Max penalty 90%


# Singleton instance
taste_reasoning = TasteReasoning()
