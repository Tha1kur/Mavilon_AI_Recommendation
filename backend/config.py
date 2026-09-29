"""
Configuration management for MAVILON AI backend.
Loads environment variables and provides centralized settings.
"""

from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Keys
    tmdb_api_key: str = "your_tmdb_api_key_here"
    
    # Server Configuration
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    frontend_url: str = "http://localhost:3000"
    
    # AI Model Configuration
    embedding_model: str = "all-MiniLM-L6-v2"
    
    # API URLs
    tmdb_base_url: str = "https://api.themoviedb.org/3"
    tmdb_image_base_url: str = "https://image.tmdb.org/t/p"
    
    # Recommendation Engine Tuning Weights
    weight_semantic_taste: float = 0.65
    weight_rating: float = 0.20
    weight_mood: float = 0.10
    weight_popularity: float = 0.05
    weight_exploration: float = 0.05
    
    # Diversity and Recency
    recency_decay_lambda: float = 0.05
    diversity_penalty_strength: float = 0.3
    
    # Logging
    log_level: str = "INFO"
    
    model_config = ConfigDict(env_file=".env", extra='allow')
    
    def is_tmdb_configured(self) -> bool:
        """Check if TMDB API key is properly configured."""
        return self.tmdb_api_key and self.tmdb_api_key != "your_tmdb_api_key_here"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
