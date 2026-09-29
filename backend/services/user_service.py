"""
User service for profile management and interaction tracking.
Handles user sessions, taste profiles, and personalization.
"""

import numpy as np
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from models.user import User, Interaction, TasteProfile, InteractionType
from models.content import Movie, Anime
from utils.logger import logger
from services.tmdb_service import tmdb_service
from sentence_transformers import SentenceTransformer
from config import get_settings
import uuid

settings = get_settings()


class UserService:
    """Service for user management and profiling."""
    
    def __init__(self):
        self.embedding_model = SentenceTransformer(settings.embedding_model)
    
    def get_or_create_user(self, db: Session, session_id: str) -> User:
        """Get existing user or create new one by session ID."""
        user = db.query(User).filter(User.session_id == session_id).first()
        
        if not user:
            user = User(session_id=session_id)
            db.add(user)
            db.commit()
            db.refresh(user)
            
            # Create empty taste profile
            taste_profile = TasteProfile(user_id=user.id)
            db.add(taste_profile)
            db.commit()
        else:
            # Update last active
            user.last_active = datetime.utcnow()
            db.commit()
        
        return user
    
    async def track_interaction(
        self,
        db: Session,
        session_id: str,
        content_id: str,
        content_type: str,
        interaction_type: InteractionType,
        mood: Optional[str] = None
    ) -> Interaction:
        """Track user interaction with content."""
        user = self.get_or_create_user(db, session_id)
        
        interaction = Interaction(
            user_id=user.id,
            content_id=content_id,
            content_type=content_type,
            interaction_type=interaction_type,
            mood=mood
        )
        
        db.add(interaction)
        db.commit()
        db.refresh(interaction)
        
        # Update taste profile asynchronously (in background)
        try:
            await self._update_taste_profile(db, user.id)
        except Exception as e:
            logger.error(f"Error triggering taste profile update: {e}", exc_info=True)
        
        return interaction
    
    def get_user_interactions(
        self,
        db: Session,
        user_id: str,
        limit: Optional[int] = None,
        days: Optional[int] = None
    ) -> List[Interaction]:
        """Get user interactions, optionally filtered by time."""
        query = db.query(Interaction).filter(Interaction.user_id == user_id)
        
        if days:
            cutoff = datetime.utcnow() - timedelta(days=days)
            query = query.filter(Interaction.timestamp >= cutoff)
        
        query = query.order_by(Interaction.timestamp.desc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def get_taste_profile(self, db: Session, user_id: str) -> Optional[TasteProfile]:
        """Get user's taste profile."""
        return db.query(TasteProfile).filter(TasteProfile.user_id == user_id).first()
    
    async def _update_taste_profile(self, db: Session, user_id: str, custom_interaction=None):
        """Update user taste profile based on interactions using EMA."""
        if custom_interaction:
            latest_interaction = custom_interaction
        else:
            # Get ONLY the most recent interaction
            interactions = self.get_user_interactions(db, user_id, limit=1)
            
            if not interactions:
                return
                
            latest_interaction = interactions[0]
        
        try:
            content = None
            if latest_interaction.content_type == "movie":
                raw_id = latest_interaction.content_id.replace("movie_", "").replace("omdb_", "")
                
                # Try TMDB lookup if numeric ID
                if raw_id.isdigit():
                    movie_id = int(raw_id)
                    movie_data = await tmdb_service.get_movie_details(movie_id)
                    if movie_data:
                        content = await tmdb_service._normalize_movie({"id": movie_id, **movie_data})
                
                if not content and not raw_id.isdigit():
                    print(f"OMDB fallback removed. Cannot fetch data for string IMDb ID {raw_id}")
            elif latest_interaction.content_type == "anime":
                # Add basic anime fetch capability when GraphQL ready
                pass
                
            if not content:
                print(f"Failed to fetch content details for {latest_interaction.content_id}")
                return
                
            # 1. Generate text and new embedding
            text_parts = [
                content.title,
                content.overview,
                f"Genres: {', '.join(content.genres) if content.genres else ''}",
            ]
            if content.mood:
                text_parts.append(f"Mood: {', '.join(content.mood)}")
                
            if content.type == "movie":
                if content.director: text_parts.append(f"Director: {content.director}")
                if content.cast: text_parts.append(f"Cast: {', '.join(content.cast)}")
            elif content.type == "anime":
                if content.studio: text_parts.append(f"Studio: {content.studio}")
                if content.characters: text_parts.append(f"Characters: {', '.join(content.characters)}")
                
            text = " ".join(filter(None, text_parts))
            new_interaction_emb = self.embedding_model.encode(text, convert_to_numpy=True)
            
            # 2. Get existing profile
            taste_profile = self.get_taste_profile(db, user_id)
            if not taste_profile:
                return
                
            # Initialize or update embedding via Exponential Moving Average (EMA)
            alpha = 0.15  # 15% weight to new interaction, 85% to history
            
            if taste_profile.taste_embedding:
                old_emb = np.array(taste_profile.taste_embedding)
                updated_emb = (old_emb * (1.0 - alpha)) + (new_interaction_emb * alpha)
            else:
                updated_emb = new_interaction_emb
                
            # 3. Update Genres & Moods using frequency dictionaries
            fav_genres = taste_profile.favorite_genres or {}
            if isinstance(fav_genres, list):
                # Backwards compatibility migration
                fav_genres = {g: 1.0 for g in fav_genres}
                
            # Decay old frequencies slightly (e.g. 5%)
            for g in fav_genres:
                fav_genres[g] *= 0.95
                
            # Add new genres
            for g in content.genres:
                fav_genres[g] = fav_genres.get(g, 0) + 1.0
                
            fav_moods = taste_profile.favorite_moods or {}
            if isinstance(fav_moods, list):
                # Backwards compatibility migration
                fav_moods = {m: 1.0 for m in fav_moods}
                
            for m in fav_moods:
                fav_moods[m] *= 0.95
                
            if content.mood:
                for m in content.mood:
                    fav_moods[m] = fav_moods.get(m, 0) + 1.0
            
            # Keep top N internally
            sorted_genres = dict(sorted(fav_genres.items(), key=lambda item: item[1], reverse=True)[:10])
            sorted_moods = dict(sorted(fav_moods.items(), key=lambda item: item[1], reverse=True)[:5])

            # 4. Save to DB
            taste_profile.taste_embedding = updated_emb.tolist()
            taste_profile.favorite_genres = sorted_genres
            taste_profile.favorite_moods = sorted_moods
            taste_profile.interaction_count += 1
            taste_profile.updated_at = datetime.utcnow()
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Error updating taste profile: {e}", exc_info=True)
            db.rollback()

    async def recalculate_taste_profile(self, db: Session, user_id: str):
        """Complete rebuild of user taste profile after a history deletion."""
        taste_profile = self.get_taste_profile(db, user_id)
        if not taste_profile:
            return
            
        # Reset profile metadata
        taste_profile.taste_embedding = None
        taste_profile.favorite_genres = {}
        taste_profile.favorite_moods = {}
        taste_profile.interaction_count = 0
        db.commit()
        
        # Get up to 15 recent interactions in chronological order (oldest -> newest)
        recent_interactions = db.query(Interaction).filter(
            Interaction.user_id == user_id
        ).order_by(Interaction.timestamp.desc()).limit(15).all()
        
        recent_interactions.reverse()
        
        # Replay the EMA sequentially
        for interaction in recent_interactions:
            await self._update_taste_profile(db, user_id, custom_interaction=interaction)

# Singleton instance
user_service = UserService()
