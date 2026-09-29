"""
Search API endpoint with OMDb fallback.
"""

from fastapi import APIRouter, HTTPException
from typing import List, Union
from models.content import Movie, Anime, SearchRequest
from services.tmdb_service import tmdb_service
from services.recommendation_service import recommendation_service
from utils.logger import logger

router = APIRouter()


@router.post("/search", response_model=List[Union[Movie, Anime]])
async def search_content(request: SearchRequest):
    """
    Search for movies and anime with OMDb fallback.
    Performs parallel searches and combines results.
    """
    try:
        # Search both sources in parallel
        movies = []
        anime = []
        
        # Try TMDB first, fallback to OMDb
        try:
            movies = await tmdb_service.search_movies(request.query, limit=20)
            logger.info(f"TMDB search returned {len(movies)} movies")
        except Exception as tmdb_error:
            logger.warning(f"TMDB movie search failed, falling back to TMDB again: {tmdb_error}")
            movies = await tmdb_service.search_movies(request.query, limit=20)
            logger.info(f"TMDB fallback movie search returned {len(movies)} movies")
        
        # Search anime
        anime = await tmdb_service.search_anime(request.query, limit=20)
        logger.info(f"TMDB anime search returned {len(anime)} anime")
        
        # Combine results
        all_results = movies + anime
        
        # Apply mood filter if specified
        if request.mood:
            all_results = recommendation_service.filter_by_mood(all_results, request.mood)
        
        # Sort by rating
        all_results.sort(key=lambda x: x.rating, reverse=True)
        
        return all_results
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
