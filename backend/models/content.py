"""
Pydantic models for content data.
Matches TypeScript interfaces from frontend.
"""

from typing import Literal, Optional, List
from pydantic import BaseModel, Field


ContentType = Literal["movie", "anime"]

Mood = Literal[
    "Dark",
    "Emotional",
    "Thriller",
    "Romance",
    "Sci-Fi",
    "Action",
    "Comedy",
    "Mystery",
    "Fantasy"
]

Genre = Literal[
    "Action",
    "Adventure",
    "Animation",
    "Comedy",
    "Crime",
    "Documentary",
    "Drama",
    "Fantasy",
    "Horror",
    "Mystery",
    "Romance",
    "Sci-Fi",
    "Thriller",
    "Psychological",
    "Supernatural",
    "Slice of Life"
]


class Movie(BaseModel):
    """Movie content model."""
    id: str
    type: Literal["movie"] = "movie"
    title: str
    posterUrl: str
    backdropUrl: Optional[str] = None
    genres: List[str]
    rating: float
    year: Optional[int] = None
    duration: Optional[int] = None  # in minutes
    overview: str
    trailerUrl: Optional[str] = None
    cast: Optional[List[str]] = None
    director: Optional[str] = None
    mood: Optional[List[str]] = None
    popularity: Optional[float] = None


class Anime(BaseModel):
    """Anime content model."""
    id: str
    type: Literal["anime"] = "anime"
    title: str
    posterUrl: str
    backdropUrl: Optional[str] = None
    genres: List[str]
    rating: float
    year: Optional[int] = None
    episodes: Optional[int] = None
    overview: str
    trailerUrl: Optional[str] = None
    characters: Optional[List[str]] = None
    studio: Optional[str] = None
    mood: Optional[List[str]] = None
    popularity: Optional[float] = None


class SearchRequest(BaseModel):
    """Search request payload."""
    query: str
    mood: Optional[str] = None


class RecommendRequest(BaseModel):
    """Recommendation request payload."""
    mood: Optional[str] = None
    limit: int = Field(default=6, ge=1, le=20)
