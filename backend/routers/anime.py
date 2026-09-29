"""
Anime API endpoints.
"""

from fastapi import APIRouter, HTTPException
from typing import List
from models.content import Anime
from services.tmdb_service import tmdb_service
from services.cache_service import cache_service

router = APIRouter()


@router.get("/trending", response_model=List[Anime])
async def get_trending_anime(limit: int = 20):
    """Get trending anime from AniList with caching."""
    try:
        # Check cache first (1 hour TTL)
        cache_key = f"trending_anime:{limit}"
        cached = cache_service.get(cache_key)
        if cached:
            return cached
        
        anime = await tmdb_service.get_trending_anime(limit=limit)
        
        # Cache the results
        cache_service.set(cache_key, anime, ttl=3600)
        
        return anime
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch trending anime: {str(e)}")
