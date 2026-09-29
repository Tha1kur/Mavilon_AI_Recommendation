"""
AI Explanation Engine for recommendations.
Generates human-readable explanations for why content is recommended.
"""

from typing import List, Optional, Dict, Any, Union
from models.content import Movie, Anime
from models.user import TasteProfile
import random


class ExplanationService:
    """Service for generating recommendation explanations."""
    
    def generate_explanation(
        self,
        content: Union[Movie, Anime],
        taste_profile: Optional[TasteProfile] = None,
        mood: Optional[str] = None,
        similar_content: Optional[List[str]] = None
    ) -> str:
        """
        Generate explanation for why content is recommended.
        
        Args:
            content: The recommended content
            taste_profile: User's taste profile (if available)
            mood: Selected mood (if any)
            similar_content: List of similar content titles user has interacted with
        
        Returns:
            Human-readable explanation string
        """
        explanations = []
        
        # Mood-based explanation
        if mood and content.mood and mood in content.mood:
            explanations.append(f"Perfect for your {mood} mood")
        
        # Taste profile-based explanation
        if taste_profile and taste_profile.favorite_genres:
            matching_genres = [g for g in content.genres if g in taste_profile.favorite_genres]
            if matching_genres:
                genre = matching_genres[0]
                explanations.append(f"Matches your taste for {genre}")
        
        # Similar content explanation
        if similar_content and len(similar_content) > 0:
            ref = similar_content[0]
            explanations.append(f"Similar to {ref}")
        
        # Genre-based explanation (fallback)
        if not explanations and content.genres:
            primary_genre = content.genres[0]
            explanations.append(f"Recommended {primary_genre}")
        
        # Rating-based boost
        if content.rating >= 8.0:
            explanations.append("Highly rated")
        
        # Combine explanations
        if len(explanations) == 0:
            return "Recommended for you"
        elif len(explanations) == 1:
            return explanations[0]
        else:
            # Take first two most relevant
            return f"{explanations[0]} • {explanations[1]}"
    
    def generate_personalized_explanation(
        self,
        content: Union[Movie, Anime],
        taste_profile: TasteProfile,
        similarity_score: float,
        mood: Optional[str] = None,
        is_exploration: bool = False
    ) -> str:
        """
        Generate personalized explanation based on taste profile and similarity.
        
        Args:
            content: The recommended content
            taste_profile: User's taste profile
            similarity_score: Similarity score (0-1)
            mood: Selected mood (if any)
            is_exploration: Whether this is an exploration recommendation
        
        Returns:
            Personalized explanation string
        """
        parts = []
        
        # Exploration takes priority
        if is_exploration:
            # Find the adjacent genre
            if taste_profile.favorite_genres and content.genres:
                matching_genres = [g for g in content.genres if g in taste_profile.favorite_genres[:3]]
                if not matching_genres:
                    # It's truly exploration
                    parts.append("Exploring a new theme you may enjoy")
        
        # High similarity with genre specificity
        if similarity_score > 0.8 and not is_exploration:
            if taste_profile.favorite_genres and content.genres:
                matching_genres = [g for g in content.genres if g in taste_profile.favorite_genres[:3]]
                if matching_genres:
                    genre = matching_genres[0]
                    parts.append(f"Strongly matches your taste for {genre}")
                else:
                    parts.append("Strongly matches your taste")
            else:
                parts.append("Strongly matches your taste")
        elif similarity_score > 0.6 and not is_exploration:
            if taste_profile.favorite_genres and content.genres:
                matching_genres = [g for g in content.genres if g in taste_profile.favorite_genres[:3]]
                if matching_genres:
                    genre = matching_genres[0]
                    parts.append(f"Matches your preference for {genre}")
                else:
                    parts.append("Matches your preferences")
            else:
                parts.append("Matches your preferences")
        
        # Favorite moods
        if mood and taste_profile.favorite_moods and mood in taste_profile.favorite_moods:
            parts.append(f"Fits your {mood} mood")
        
        # Interaction count context
        if taste_profile.interaction_count > 20:
            parts.append("Based on your extensive viewing history")
        elif taste_profile.interaction_count > 10 and not is_exploration:
            parts.append("Based on your viewing history")
        elif taste_profile.interaction_count > 0 and taste_profile.interaction_count <= 10:
            parts.append("Learning your taste")
        
        # Combine parts
        if len(parts) == 0:
            return "Recommended for you"
        elif len(parts) == 1:
            return parts[0]
        else:
            # Take first two
            return f"{parts[0]} • {parts[1]}"



# Singleton instance
explanation_service = ExplanationService()
