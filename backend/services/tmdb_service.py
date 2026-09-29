"""
TMDB API service for fetching movie data.
Handles API communication and data normalization.
"""

import httpx
import os
import asyncio
from typing import List, Optional, Dict, Any
from config import get_settings
from models.content import Movie, Anime
from utils.logger import logger

settings = get_settings()


class TMDBService:
    """Service for interacting with TMDB API."""
    
    def __init__(self):
        self.base_url = settings.tmdb_base_url
        self.api_key = os.getenv("TMDB_API_KEY")
        self.image_base_url = settings.tmdb_image_base_url
        self._is_configured = settings.is_tmdb_configured()
        
        if not self._is_configured:
            print("⚠️  TMDB API key not configured - movie endpoints will use fallback")
    
    def _check_configured(self):
        """Raise error if API key is not configured."""
        if not self._is_configured:
            raise ValueError(
                "TMDB API key not configured. "
                "Please set TMDB_API_KEY in backend/.env file. "
                "Get your free API key at: https://www.themoviedb.org/settings/api"
            )
        
    async def get_trending_movies(self, limit: int = 20) -> List[Movie]:
        """Fetch trending movies from TMDB."""
        self._check_configured()  # Validate API key is configured
        
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{self.base_url}/trending/movie/week",
                    params={"api_key": self.api_key}
                )
                response.raise_for_status()
                data = response.json()
        except httpx.RequestError as e:
            logger.warning(f"TMDB request failed for trending movies: {e}")
            return []
            
        semaphore = asyncio.Semaphore(5)
        
        async def process_item(item):
            async with semaphore:
                return await self._normalize_movie(item)
                
        tasks = [process_item(item) for item in data.get("results", [])[:limit]]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        movies = [m for m in results if m and not isinstance(m, Exception)]
        return movies
    
    async def search_movies(self, query: str, limit: int = 10) -> List[Movie]:
        """Search for movies by query."""
        self._check_configured()  # Validate API key is configured
        
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{self.base_url}/search/movie",
                    params={
                        "api_key": self.api_key,
                        "query": query,
                        "include_adult": False
                    }
                )
                response.raise_for_status()
                data = response.json()
        except httpx.RequestError as e:
            logger.warning(f"TMDB request failed for search query '{query}': {e}")
            return []
            
        semaphore = asyncio.Semaphore(5)
        
        async def process_item(item):
            async with semaphore:
                return await self._normalize_movie(item)
                
        tasks = [process_item(item) for item in data.get("results", [])[:limit]]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        movies = [m for m in results if m and not isinstance(m, Exception)]
        return movies
    
    async def get_movie_details(self, movie_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed movie information including credits and videos."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                # Get movie details
                response = await client.get(
                    f"{self.base_url}/movie/{movie_id}",
                    params={
                        "api_key": self.api_key,
                        "append_to_response": "credits,videos,recommendations,similar"
                    }
                )
                response.raise_for_status()
                return response.json()
        except httpx.RequestError as e:
            logger.warning(f"TMDB request failed for movie details ID {movie_id}: {e}")
            return None
    
    async def get_trending_anime(self, limit: int = 20) -> List[Anime]:
        """Fetch trending anime from TMDB (TV shows with Animation genre and JP language)."""
        self._check_configured()
        
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{self.base_url}/discover/tv",
                    params={
                        "api_key": self.api_key,
                        "with_genres": "16",
                        "with_original_language": "ja",
                        "sort_by": "popularity.desc"
                    }
                )
                response.raise_for_status()
                data = response.json()
        except httpx.RequestError as e:
            logger.warning(f"TMDB request failed for trending anime: {e}")
            return []
            
        semaphore = asyncio.Semaphore(5)
        
        async def process_item(item):
            async with semaphore:
                return await self._normalize_anime(item)
                
        tasks = [process_item(item) for item in data.get("results", [])[:limit]]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        anime_list = [a for a in results if a and not isinstance(a, Exception)]
        return anime_list
        
    async def search_anime(self, query: str, limit: int = 10) -> List[Anime]:
        """Search for anime by query in TMDB TV shows."""
        self._check_configured()
        
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{self.base_url}/search/tv",
                    params={
                        "api_key": self.api_key,
                        "query": query,
                        "include_adult": False
                    }
                )
                response.raise_for_status()
                data = response.json()
        except httpx.RequestError as e:
            logger.warning(f"TMDB request failed for search query '{query}': {e}")
            return []
            
        semaphore = asyncio.Semaphore(5)
        
        async def process_item(item):
            # Only include Japanese animation
            if item.get("original_language") == "ja" and 16 in item.get("genre_ids", []):
                async with semaphore:
                    return await self._normalize_anime(item)
            return None
            
        tasks = [process_item(item) for item in data.get("results", [])]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        anime_list = [a for a in results if a and not isinstance(a, Exception)]
        return anime_list[:limit]
        
    async def get_anime_details(self, anime_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed TV/anime information including credits and videos."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{self.base_url}/tv/{anime_id}",
                    params={
                        "api_key": self.api_key,
                        "append_to_response": "credits,videos,recommendations,similar"
                    }
                )
                response.raise_for_status()
                return response.json()
        except httpx.RequestError as e:
            logger.warning(f"TMDB request failed for anime details ID {anime_id}: {e}")
            return None
            
    async def _normalize_movie(self, tmdb_data: Dict[str, Any]) -> Optional[Movie]:
        """Normalize TMDB movie data to our Movie model."""
        try:
            movie_id = tmdb_data.get("id")
            
            # Get detailed info for cast, director, and trailer
            details = await self.get_movie_details(movie_id)
            
            if details is None:
                return None
            
            # Extract genres
            genres = []
            if "genres" in details:
                genres = [g["name"] for g in details["genres"]]
            elif "genre_ids" in tmdb_data:
                # Map genre IDs to names (common TMDB genres)
                genre_map = {
                    28: "Action", 12: "Adventure", 16: "Animation",
                    35: "Comedy", 80: "Crime", 99: "Documentary",
                    18: "Drama", 10751: "Family", 14: "Fantasy",
                    36: "History", 27: "Horror", 10402: "Music",
                    9648: "Mystery", 10749: "Romance", 878: "Sci-Fi",
                    10770: "TV Movie", 53: "Thriller", 10752: "War",
                    37: "Western"
                }
                genres = [genre_map.get(gid, "Unknown") for gid in tmdb_data["genre_ids"] if gid in genre_map]
            
            # Extract cast (top 5)
            cast = []
            if "credits" in details and "cast" in details["credits"]:
                cast = [actor["name"] for actor in details["credits"]["cast"][:5]]
            
            # Extract director
            director = None
            if "credits" in details and "crew" in details["credits"]:
                directors = [person["name"] for person in details["credits"]["crew"] if person["job"] == "Director"]
                director = directors[0] if directors else None
            
            # Extract trailer
            trailer_url = None
            if "videos" in details and "results" in details["videos"]:
                youtube_videos = [v for v in details["videos"]["results"] if v["site"] == "YouTube" and v["type"] == "Trailer"]
                if youtube_videos:
                    trailer_url = f"https://www.youtube.com/watch?v={youtube_videos[0]['key']}"
            
            # Build poster and backdrop URLs
            poster_path = tmdb_data.get("poster_path") or details.get("poster_path")
            backdrop_path = tmdb_data.get("backdrop_path") or details.get("backdrop_path")
            
            poster_url = f"{self.image_base_url}/w500{poster_path}" if poster_path else ""
            backdrop_url = f"{self.image_base_url}/original{backdrop_path}" if backdrop_path else None
            
            # Get release year
            release_date = tmdb_data.get("release_date") or details.get("release_date", "")
            year = int(release_date[:4]) if release_date and len(release_date) >= 4 else 0
            
            # Map genres to moods
            mood = self._map_genres_to_moods(genres)
            
            # Extract popularity
            popularity = tmdb_data.get("popularity", 0.0)
            if not popularity and details:
                popularity = details.get("popularity", 0.0)
            
            return Movie(
                id=f"movie_{movie_id}",
                title=tmdb_data.get("title", "Unknown"),
                posterUrl=poster_url,
                backdropUrl=backdrop_url,
                genres=genres,
                rating=round(tmdb_data.get("vote_average", 0.0), 1),
                year=year if year else None,
                duration=details.get("runtime") if details.get("runtime") else None,
                overview=tmdb_data.get("overview", ""),
                trailerUrl=trailer_url,
                cast=cast if cast else None,
                director=director,
                mood=mood if mood else None,
                popularity=float(popularity) if popularity else None
            )
        except Exception as e:
            logger.error(f"Error normalizing movie {tmdb_data.get('id')}: {e}", exc_info=True)
            return None
            
    async def _normalize_anime(self, tmdb_data: Dict[str, Any]) -> Optional[Anime]:
        """Normalize TMDB TV data to our Anime model."""
        try:
            anime_id = tmdb_data.get("id")
            
            # Get detailed info
            details = await self.get_anime_details(anime_id)
            
            if details is None:
                return None
            
            # Extract genres
            genres = []
            if "genres" in details:
                genres = [g["name"] for g in details["genres"]]
            elif "genre_ids" in tmdb_data:
                genre_map = {16: "Animation", 10759: "Action & Adventure", 35: "Comedy", 18: "Drama", 10765: "Sci-Fi & Fantasy", 9648: "Mystery"}
                genres = [genre_map.get(gid, "Unknown") for gid in tmdb_data["genre_ids"] if gid in genre_map]
            
            # Extract characters/cast (top 5)
            characters = []
            if "credits" in details and "cast" in details["credits"]:
                characters = [actor["name"] for actor in details["credits"]["cast"][:5]]
            
            # Extract studio (networks/production_companies)
            studio = None
            if "networks" in details and details["networks"]:
                studio = details["networks"][0]["name"]
            elif "production_companies" in details and details["production_companies"]:
                studio = details["production_companies"][0]["name"]
            
            # Extract trailer
            trailer_url = None
            if "videos" in details and "results" in details["videos"]:
                youtube_videos = [v for v in details["videos"]["results"] if v["site"] == "YouTube" and v["type"] == "Trailer"]
                if youtube_videos:
                    trailer_url = f"https://www.youtube.com/embed/{youtube_videos[0]['key']}"
            
            # Build URLs
            poster_path = tmdb_data.get("poster_path") or details.get("poster_path")
            backdrop_path = tmdb_data.get("backdrop_path") or details.get("backdrop_path")
            
            poster_url = f"{self.image_base_url}/w500{poster_path}" if poster_path else ""
            backdrop_url = f"{self.image_base_url}/original{backdrop_path}" if backdrop_path else None
            
            # Get release year
            first_air_date = tmdb_data.get("first_air_date") or details.get("first_air_date", "")
            year = int(first_air_date[:4]) if first_air_date and len(first_air_date) >= 4 else 0
            
            # Map genres to moods
            mood = self._map_genres_to_moods(genres)
            
            # Extract popularity
            popularity = tmdb_data.get("popularity", 0.0)
            if not popularity and details:
                popularity = details.get("popularity", 0.0)
                
            # Get episodes
            episodes = details.get("number_of_episodes")
            
            return Anime(
                id=f"anime_{anime_id}",
                title=tmdb_data.get("name", tmdb_data.get("original_name", "Unknown")),
                posterUrl=poster_url,
                backdropUrl=backdrop_url,
                genres=genres,
                rating=round(tmdb_data.get("vote_average", 0.0), 1),
                year=year if year else None,
                episodes=episodes,
                overview=tmdb_data.get("overview", ""),
                trailerUrl=trailer_url,
                characters=characters if characters else None,
                studio=studio,
                mood=mood if mood else None,
                popularity=float(popularity) if popularity else None
            )
        except Exception as e:
            logger.error(f"Error normalizing anime {tmdb_data.get('id')}: {e}", exc_info=True)
            return None
    
    def _map_genres_to_moods(self, genres: List[str]) -> List[str]:
        """Map genres to mood categories."""
        mood_mapping = {
            "Dark": ["Horror", "Thriller", "Mystery", "Crime"],
            "Emotional": ["Drama", "Romance"],
            "Thriller": ["Thriller", "Mystery", "Crime"],
            "Romance": ["Romance"],
            "Sci-Fi": ["Sci-Fi", "Fantasy"],
            "Action": ["Action", "Adventure"],
            "Comedy": ["Comedy"]
        }
        
        moods = set()
        for mood, mood_genres in mood_mapping.items():
            if any(genre in genres for genre in mood_genres):
                moods.add(mood)
        
        return list(moods)


# Singleton instance
tmdb_service = TMDBService()
