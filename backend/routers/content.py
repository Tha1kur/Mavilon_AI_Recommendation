"""
Content detail API endpoints.
Provides detailed information about movies and anime.
"""

from fastapi import APIRouter, HTTPException
from typing import Union, List
from models.content import Movie, Anime
from models.content import Movie, Anime
from services.tmdb_service import tmdb_service
from services.recommendation_service import recommendation_service
from services.cache_service import cache_service

router = APIRouter()


@router.get("/content/{content_type}/{content_id}")
async def get_content_details(
    content_type: str,
    content_id: str
):
    """
    Get detailed information about a specific content item.
    
    Args:
        content_type: 'movie' or 'anime'
        content_id: Content ID (e.g., 'movie_550' or 'anime_1')
    """
    try:
        # Check cache first
        cache_key = f"content_detail:{content_type}:{content_id}"
        cached = cache_service.get(cache_key)
        if cached:
            return cached
        
        # Extract ID safely without assuming int
        if content_type in ["movie", "anime"]:
            raw_id = content_id.replace("movie_", "").replace("anime_", "")
            
            if not raw_id.isdigit():
                raise HTTPException(status_code=400, detail="Invalid TMDB numeric ID for content")
                
            tmdb_id = int(raw_id)
            
            # Use TMDB specific fetcher depending on type
            if content_type == "movie":
                details = await tmdb_service.get_movie_details(tmdb_id)
            else:
                details = await tmdb_service.get_anime_details(tmdb_id)
                
            if not details:
                raise HTTPException(status_code=404, detail=f"{content_type.capitalize()} not found")
            
            # Normalize to respective model object
            if content_type == "movie":
                content = await tmdb_service._normalize_movie({"id": tmdb_id, **details})
            else:
                content = await tmdb_service._normalize_anime({"id": tmdb_id, **details})
            
            # Extract similar / recommendations
            similar_raw = details.get("recommendations", {}).get("results", [])
            if not similar_raw:
                similar_raw = details.get("similar", {}).get("results", [])
                
            similar_items = []
            for item in similar_raw[:6]:
                if content_type == "movie":
                    sim_content = await tmdb_service._normalize_movie(item)
                else:
                    sim_content = await tmdb_service._normalize_anime(item)
                    
                if sim_content:
                    similar_items.append(sim_content.dict())
            
            # Convert to dict and embed similar
            result = content.dict()
            result["similar"] = similar_items
            
            # Map standard fields required by prompt for Unified Model if needed
            # "description" is "overview" in our model, "poster_url" is "posterUrl"
            result["description"] = result.get("overview", "")
            result["poster_url"] = result.get("posterUrl", "")
            result["backdrop_url"] = result.get("backdropUrl", "")
            result["trailer_url"] = result.get("trailerUrl")
            
        else:
            raise HTTPException(status_code=400, detail="Invalid content type. Use 'movie' or 'anime'")
        
        # Cache for 1 hour
        cache_service.set(cache_key, result, ttl=3600)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get content details: {str(e)}")


@router.get("/content/{content_type}/{content_id}/similar")
async def get_similar_content(
    content_type: str,
    content_id: str,
    limit: int = 10
):
    """
    Get similar content using AI similarity.
    
    Args:
        content_type: 'movie' or 'anime'
        content_id: Content ID
        limit: Number of similar items to return
    """
    try:
        # Get the target content
        target_content = await get_content_details(content_type, content_id)
        
        # Fetch pool of content
        movies = await tmdb_service.get_trending_movies(limit=30)
        anime = await tmdb_service.get_trending_anime(limit=30)
        all_content = movies + anime
        
        # Find similar content
        similar = recommendation_service.get_similar_content(
            target=target_content,
            candidates=all_content,
            limit=limit
        )
        
        return similar
        
    except HTTPException:
        return []
    except Exception as e:
        # Instead of failing the entire section on the frontend, we return an empty list if this feature errors.
        print(f"Failed to get similar content: {str(e)}")
        return []
