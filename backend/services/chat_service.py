"""
AI chat assistant for natural language content discovery.
Processes queries and returns personalized recommendations.
"""

from typing import List, Dict, Any, Optional, Union
import re
from models.content import Movie, Anime
from services.recommendation_service import recommendation_service
from services.explanation_service import explanation_service


class ChatService:
    """Natural language query processing for content discovery."""
    
    def __init__(self):
        # Mood keywords mapping
        self.mood_keywords = {
            "Dark": ["dark", "gritty", "noir", "grim", "sinister", "disturbing"],
            "Emotional": ["emotional", "touching", "heartfelt", "moving", "tear-jerker"],
            "Thriller": ["thriller", "suspense", "tense", "gripping", "edge"],
            "Romance": ["romance", "romantic", "love", "relationship"],
            "Sci-Fi": ["sci-fi", "science fiction", "futuristic", "space", "cyberpunk"],
            "Action": ["action", "explosive", "intense", "adrenaline"],
            "Comedy": ["comedy", "funny", "hilarious", "humor", "laugh"],
            "Mystery": ["mystery", "detective", "whodunit", "puzzle"],
            "Fantasy": ["fantasy", "magical", "epic", "adventure"]
        }
        
        # Genre keywords
        self.genre_keywords = {
            "Horror": ["horror", "scary", "terrifying", "creepy"],
            "Drama": ["drama", "dramatic", "serious"],
            "Psychological": ["psychological", "mind-bending", "cerebral"],
            "Supernatural": ["supernatural", "paranormal", "ghost"],
            "Crime": ["crime", "criminal", "heist", "mafia"]
        }
    
    async def process_query(
        self,
        query: str,
        all_content: List[Union[Movie, Anime]],
        user_taste_embedding: Optional[Any] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Process natural language query and return recommendations.
        
        Args:
            query: Natural language query
            all_content: Pool of content to search
            user_taste_embedding: Optional user taste for personalization
            limit: Number of results to return
        
        Returns:
            Dict with response message and ranked results
        """
        query_lower = query.lower()
        
        # Extract mood from query
        detected_mood = self._extract_mood(query_lower)
        
        # Extract genres from query
        detected_genres = self._extract_genres(query_lower)
        
        # Check for "like X" pattern to find similar content
        similar_to = self._extract_similar_to(query_lower, all_content)
        
        # Build response message
        response_parts = []
        if detected_mood:
            response_parts.append(f"{detected_mood} mood")
        if detected_genres:
            response_parts.append(f"{', '.join(detected_genres)} genres")
        if similar_to:
            response_parts.append(f"similar to {similar_to.title}")
        
        if response_parts:
            response_message = f"Here are recommendations for {' with '.join(response_parts)}:"
        else:
            response_message = "Here are some recommendations based on your query:"
        
        # Get recommendations
        if similar_to:
            # Find similar content
            recommendations = recommendation_service.get_similar_content(
                target=similar_to,
                candidates=all_content,
                limit=limit
            )
            results = [(content, 0.8) for content in recommendations]
        elif user_taste_embedding is not None:
            # Personalized recommendations
            results = recommendation_service.get_personalized_recommendations(
                all_content=all_content,
                user_taste_embedding=user_taste_embedding,
                mood=detected_mood,
                limit=limit,
                ensure_diversity=True
            )
        else:
            # Generic recommendations
            filtered_content = all_content
            
            # Filter by mood
            if detected_mood:
                filtered_content = recommendation_service.filter_by_mood(filtered_content, detected_mood)
            
            # Filter by genres
            if detected_genres:
                filtered_content = [
                    c for c in filtered_content
                    if any(genre in c.genres for genre in detected_genres)
                ]
            
            # Sort by rating
            filtered_content.sort(key=lambda x: x.rating, reverse=True)
            results = [(content, 0.7) for content in filtered_content[:limit]]
        
        # Generate explanations
        formatted_results = []
        for item in results:
            content = item[0]
            score = item[1]
            explanation = self._generate_chat_explanation(
                content, detected_mood, detected_genres, similar_to
            )
            
            formatted_results.append({
                "content": content,
                "explanation": explanation,
                "score": score
            })
        
        return {
            "response": response_message,
            "results": formatted_results,
            "detected_mood": detected_mood,
            "detected_genres": detected_genres
        }
    
    def _extract_mood(self, query: str) -> Optional[str]:
        """Extract mood from query text."""
        for mood, keywords in self.mood_keywords.items():
            if any(keyword in query for keyword in keywords):
                return mood
        return None
    
    def _extract_genres(self, query: str) -> List[str]:
        """Extract genres from query text."""
        genres = []
        for genre, keywords in self.genre_keywords.items():
            if any(keyword in query for keyword in keywords):
                genres.append(genre)
        return genres
    
    def _extract_similar_to(
        self,
        query: str,
        all_content: List[Union[Movie, Anime]]
    ) -> Optional[Union[Movie, Anime]]:
        """Extract 'like X' pattern and find matching content."""
        # Pattern: "like X", "similar to X", "movies like X"
        patterns = [
            r"like\s+([a-zA-Z0-9\s]+?)(?:\s+but|\s+with|\s*$)",
            r"similar\s+to\s+([a-zA-Z0-9\s]+?)(?:\s+but|\s+with|\s*$)",
            r"(?:movies?|anime)\s+like\s+([a-zA-Z0-9\s]+?)(?:\s+but|\s+with|\s*$)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                title_query = match.group(1).strip()
                
                # Find matching content
                for content in all_content:
                    if title_query.lower() in content.title.lower():
                        return content
        
        return None
    
    def _generate_chat_explanation(
        self,
        content: Union[Movie, Anime],
        mood: Optional[str],
        genres: List[str],
        similar_to: Optional[Union[Movie, Anime]]
    ) -> str:
        """Generate explanation for chat results."""
        parts = []
        
        if similar_to:
            parts.append(f"Similar to {similar_to.title}")
        
        if mood and content.mood and mood in content.mood:
            parts.append(f"Matches {mood} mood")
        
        if genres:
            matching_genres = [g for g in genres if g in content.genres]
            if matching_genres:
                parts.append(f"{', '.join(matching_genres)} genre")
        
        if content.rating >= 8.0:
            parts.append(f"Highly rated ({content.rating}/10)")
        
        if not parts:
            parts.append("Recommended for you")
        
        return " • ".join(parts[:2])  # Max 2 parts


# Singleton instance
chat_service = ChatService()
