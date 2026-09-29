"""
Movie API endpoints with OMDb fallback.
"""

from fastapi import APIRouter, HTTPException
from typing import List
from models.content import Movie
from services.tmdb_service import tmdb_service
from services.cache_service import cache_service
from utils.logger import logger

router = APIRouter()


@router.get("/trending", response_model=List[Movie])
async def get_trending_movies(limit: int = 20):
    """Get trending movies from TMDB with OMDb fallback and caching."""
    try:
        # Check cache first (1 hour TTL)
        cache_key = f"trending_movies:{limit}"
        cached = cache_service.get(cache_key)
        if cached:
            logger.info(f"Returning cached trending movies (limit={limit})")
            return cached
        
        # Try TMDB first
        try:
            movies = await tmdb_service.get_trending_movies(limit=limit)
            if movies:
                logger.info(f"Fetched {len(movies)} trending movies from TMDB")
                cache_service.set(cache_key, movies, ttl=3600)
                return movies
        except ValueError as config_error:
            # TMDB not configured - this is expected, log as info
            logger.info(f"TMDB not configured, using OMDb fallback: {config_error}")
        except Exception as tmdb_error:
            # TMDB API error - log as warning
            logger.warning(f"TMDB API failed, falling back to OMDb: {tmdb_error}")
        
        # Fallback to OMDb
        movies = await tmdb_service.get_popular_movies(limit=limit)
        if movies:
            logger.info(f"Fetched {len(movies)} popular movies from OMDb (fallback)")
            cache_service.set(cache_key, movies, ttl=3600)
            return movies
        
        # Both failed
        raise HTTPException(
            status_code=503,
            detail={
                "error": "Movie data unavailable",
                "message": "Both TMDB and OMDb are unavailable. Please configure API keys.",
                "setup_instructions": {
                    "tmdb": "Get free API key at https://www.themoviedb.org/settings/api",
                    "omdb": "Get free API key at http://www.omdbapi.com/apikey.aspx"
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch trending movies: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch trending movies: {str(e)}")
