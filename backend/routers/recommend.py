"""
Recommendation API endpoint with personalization support.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Union, Optional
from pydantic import BaseModel
from models.content import Movie, Anime, RecommendRequest
from models.content import Movie, Anime, RecommendRequest
from services.tmdb_service import tmdb_service
from services.recommendation_service import recommendation_service
from services.user_service import user_service
from services.explanation_service import explanation_service
from database import get_db
from utils.logger import logger
import numpy as np

router = APIRouter()


class RecommendationWithExplanation(BaseModel):
    """Recommendation with AI explanation."""
    content: Union[Movie, Anime]
    explanation: str
    score: float


@router.post("/recommend", response_model=List[RecommendationWithExplanation])
async def get_recommendations(
    request: RecommendRequest,
    session_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get AI-powered recommendations with personalization.
    Uses content-based filtering combined with user taste.
    """
    try:
        # Fetch trending content from TMDB (both movies and anime)
        try:
            movies = await tmdb_service.get_trending_movies(limit=30)
            anime = await tmdb_service.get_trending_anime(limit=30)
        except Exception as tmdb_error:
            logger.error(f"TMDB unavailable for recommendations: {tmdb_error}", exc_info=True)
            raise HTTPException(status_code=503, detail="Recommendation engine temporarily unavailable")
        
        # Combine all content
        all_content = movies + anime
        
        if not all_content:
            raise HTTPException(status_code=503, detail="No content available for recommendations")
        
        # Get user taste profile if session provided
        user_taste_embedding = None
        taste_profile = None
        
        if session_id:
            try:
                user = user_service.get_or_create_user(db, session_id)
                taste_profile = user_service.get_taste_profile(db, user.id)
                
                if taste_profile and taste_profile.taste_embedding:
                    user_taste_embedding = np.array(taste_profile.taste_embedding)
            except Exception as e:
                print(f"Error loading user profile: {e}")
                # Continue without personalization
        
        # Get recommendations (personalized if user taste available)
        if user_taste_embedding is not None:
            # Personalized recommendations with taste reasoning
            recommendations_with_scores = recommendation_service.get_personalized_recommendations(
                all_content=all_content,
                user_taste_embedding=user_taste_embedding,
                mood=request.mood,
                limit=request.limit,
                ensure_diversity=True,
                interaction_count=taste_profile.interaction_count if taste_profile else 0,
                favorite_genres=taste_profile.favorite_genres if taste_profile else None,
                favorite_moods=taste_profile.favorite_moods if taste_profile else None
            )
        else:
            # Regular recommendations
            regular_recs = recommendation_service.get_recommendations(
                all_content=all_content,
                mood=request.mood,
                limit=request.limit,
                ensure_diversity=True
            )
            recommendations_with_scores = [(content, 0.5, False) for content in regular_recs]
        
        # Generate explanations for each recommendation
        results = []
        for content, score, is_exploration in recommendations_with_scores:
            if taste_profile and user_taste_embedding is not None:
                # Personalized explanation
                explanation = explanation_service.generate_personalized_explanation(
                    content=content,
                    taste_profile=taste_profile,
                    similarity_score=score,
                    mood=request.mood,
                    is_exploration=is_exploration
                )
            else:
                # Generic explanation
                explanation = explanation_service.generate_explanation(
                    content=content,
                    mood=request.mood
                )
            
            results.append(RecommendationWithExplanation(
                content=content,
                explanation=explanation,
                score=score
            ))
        
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Recommendation failed: {e}", exc_info=True)
        raise HTTPException(status_code=503, detail="Recommendation engine temporarily unavailable")
