"""
AI chat assistant API endpoint.
Processes natural language queries for content discovery.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Union
import numpy as np
from database import get_db
from services.chat_service import chat_service
from services.tmdb_service import tmdb_service
from services.user_service import user_service
from models.content import Movie, Anime

router = APIRouter()


class ChatRequest(BaseModel):
    """Chat query request."""
    query: str
    session_id: Optional[str] = None
    limit: int = 10


class ChatResult(BaseModel):
    """Chat result item."""
    content: Union[Movie, Anime]
    explanation: str
    score: float


class ChatResponse(BaseModel):
    """Chat response."""
    response: str
    results: List[ChatResult]
    detected_mood: Optional[str] = None
    detected_genres: Optional[List[str]] = None


@router.post("/chat", response_model=ChatResponse)
async def chat_query(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    Process natural language query for content discovery.
    
    Examples:
    - "Recommend dark psychological anime"
    - "Find movies like Interstellar but darker"
    - "Happy ending romance with comedy"
    """
    try:
        # Fetch content from TMDB (both movies and anime)
        movies = await tmdb_service.get_trending_movies(limit=30)
        anime = await tmdb_service.get_trending_anime(limit=30)
        all_content = movies + anime
        
        if not all_content:
            raise HTTPException(status_code=503, detail="No content available")
        
        # Get user taste if session provided
        user_taste_embedding = None
        if request.session_id:
            try:
                user = user_service.get_or_create_user(db, request.session_id)
                taste_profile = user_service.get_taste_profile(db, user.id)
                
                if taste_profile and taste_profile.taste_embedding:
                    user_taste_embedding = np.array(taste_profile.taste_embedding)
            except Exception as e:
                print(f"Error loading user profile: {e}")
        
        # Process query with try/except for timeout/errors
        try:
            import asyncio
            # Wrap the chat processing call with a timeout to prevent hanging, awaiting it
            result = await asyncio.wait_for(
                chat_service.process_query(
                    query=request.query,
                    all_content=all_content,
                    user_taste_embedding=user_taste_embedding,
                    limit=request.limit
                ),
                timeout=10.0
            )
        except asyncio.TimeoutError:
            raise HTTPException(status_code=503, detail="AI service temporarily unavailable")
        except Exception as e:
            from utils.logger import logger
            logger.error(f"Chat service failed: {e}", exc_info=True)
            raise HTTPException(status_code=503, detail="AI service temporarily unavailable")
        
        # Format response
        return ChatResponse(
            response=result["response"],
            results=[
                ChatResult(
                    content=item["content"],
                    explanation=item["explanation"],
                    score=item["score"]
                )
                for item in result["results"]
            ],
            detected_mood=result.get("detected_mood"),
            detected_genres=result.get("detected_genres")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat query failed: {str(e)}")
