"""
AI-powered recommendation service using sentence transformers.
Implements content-based filtering with semantic similarity.
"""

import numpy as np
from typing import List, Dict, Optional, Union, Tuple
from sentence_transformers import SentenceTransformer
import threading
import time
from models.content import Movie, Anime
from config import get_settings
from utils.logger import logger

settings = get_settings()


class RecommendationService:
    """AI recommendation engine using text embeddings."""
    
    def __init__(self):
        """Initialize the recommendation service."""
        self.model: Optional[SentenceTransformer] = None
        self.embeddings_cache: Dict[str, np.ndarray] = {}
        self._is_loading = False
        self._load_error = None
        logger.info("RecommendationService initialized (model not loaded yet)")
        
    @property
    def is_model_ready(self) -> bool:
        """Check if the AI model is loaded and ready."""
        return self.model is not None

    def load_model(self):
        """Load the embedding model in a separate thread."""
        if self.is_model_ready or self._is_loading:
            return

        self._is_loading = True
        
        def _load():
            try:
                logger.info(f"Loading embedding model: {settings.embedding_model}...")
                start_time = time.time()
                self.model = SentenceTransformer(settings.embedding_model)
                duration = time.time() - start_time
                logger.info(f"✓ AI Model loaded successfully in {duration:.2f}s")
            except Exception as e:
                logger.error(f"Failed to load AI model: {e}")
                self._load_error = str(e)
            finally:
                self._is_loading = False

        thread = threading.Thread(target=_load, daemon=True)
        thread.start()
        
    def _get_content_text(self, content: Union[Movie, Anime]) -> str:
        """Extract text representation of content for embedding."""
        # Combine title, overview, genres, cast, director,/studio for deep semantic representation
        genres_text = ", ".join(content.genres) if content.genres else ""
        mood_text = ", ".join(content.mood) if content.mood else ""
        
        text_parts = [
            content.title,
            content.overview,
            f"Genres: {genres_text}",
        ]
        
        if mood_text:
            text_parts.append(f"Mood: {mood_text}")
            
        if content.type == "movie":
            if content.director:
                text_parts.append(f"Director: {content.director}")
            if content.cast:
                text_parts.append(f"Cast: {', '.join(content.cast)}")
        elif content.type == "anime":
            if content.studio:
                text_parts.append(f"Studio: {content.studio}")
            if content.characters:
                text_parts.append(f"Characters: {', '.join(content.characters)}")
        
        return " ".join(filter(None, text_parts))
    
    def _get_embedding(self, content: Union[Movie, Anime]) -> Optional[np.ndarray]:
        """Get or compute embedding for content."""
        if not self.is_model_ready:
            return None
            
        content_id = content.id
        
        # Check cache first
        if content_id in self.embeddings_cache:
            return self.embeddings_cache[content_id]
        
        # Compute embedding
        try:
            text = self._get_content_text(content)
            embedding = self.model.encode(text, convert_to_numpy=True)
            
            # Cache for future use
            self.embeddings_cache[content_id] = embedding
            
            return embedding
        except Exception as e:
            logger.error(f"Error computing embedding for {content_id}: {e}")
            return None
    
    def compute_similarity(
        self,
        content1: Union[Movie, Anime],
        content2: Union[Movie, Anime]
    ) -> float:
        """Compute cosine similarity between two content items."""
        if not self.is_model_ready:
            return 0.0
            
        emb1 = self._get_embedding(content1)
        emb2 = self._get_embedding(content2)
        
        if emb1 is None or emb2 is None:
            return 0.0
        
        # Cosine similarity
        try:
            similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
            return float(similarity)
        except Exception:
            return 0.0
    
    def get_similar_content(
        self,
        target: Union[Movie, Anime],
        candidates: List[Union[Movie, Anime]],
        limit: int = 10
    ) -> List[Union[Movie, Anime]]:
        """Find similar content to target from candidates."""
        if not self.is_model_ready:
            logger.warning("AI model not ready, returning empty similarities")
            return []
            
        target_embedding = self._get_embedding(target)
        if target_embedding is None:
            return []
        
        # Compute similarities
        similarities = []
        for candidate in candidates:
            if candidate.id == target.id:
                continue  # Skip self
            
            candidate_embedding = self._get_embedding(candidate)
            if candidate_embedding is not None:
                similarity = np.dot(target_embedding, candidate_embedding) / (
                    np.linalg.norm(target_embedding) * np.linalg.norm(candidate_embedding)
                )
                similarities.append((candidate, float(similarity)))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Return top N
        return [content for content, _ in similarities[:limit]]
    
    def filter_by_mood(
        self,
        content_list: List[Union[Movie, Anime]],
        mood: str
    ) -> List[Union[Movie, Anime]]:
        """Filter content by mood preference."""
        # Mood to genre mapping
        mood_genre_map = {
            "Dark": ["Horror", "Thriller", "Mystery", "Psychological", "Crime"],
            "Emotional": ["Drama", "Romance"],
            "Thriller": ["Thriller", "Mystery", "Crime"],
            "Romance": ["Romance", "Drama"],
            "Sci-Fi": ["Sci-Fi", "Fantasy", "Mecha"],
            "Action": ["Action", "Adventure"],
            "Comedy": ["Comedy", "Slice of Life"]
        }
        
        target_genres = mood_genre_map.get(mood, [])
        if not target_genres:
            return content_list
        
        # Filter content that has at least one matching genre
        filtered = []
        for content in content_list:
            if any(genre in content.genres for genre in target_genres):
                filtered.append(content)
        
        return filtered
    
    def get_recommendations(
        self,
        all_content: List[Union[Movie, Anime]],
        mood: Optional[str] = None,
        limit: int = 6,
        ensure_diversity: bool = True
    ) -> List[Union[Movie, Anime]]:
        """Get AI-powered recommendations."""
        # Filter by mood if specified
        if mood:
            content_pool = self.filter_by_mood(all_content, mood)
            if not content_pool:
                content_pool = all_content  # Fallback to all if no matches
        else:
            content_pool = all_content
        
        if not content_pool:
            return []
        
        # If model is not ready, return random/popular selection
        if not self.is_model_ready:
            # Sort by rating as fallback
            sorted_content = sorted(content_pool, key=lambda x: x.rating, reverse=True)
            return sorted_content[:limit]
        
        # If we have fewer items than requested, return all
        if len(content_pool) <= limit:
            return content_pool
        
        # Use embedding-based diversity selection
        recommendations = self._select_diverse_content(content_pool, limit, ensure_diversity)
        
        return recommendations
    
    def _select_diverse_content(
        self,
        content_pool: List[Union[Movie, Anime]],
        limit: int,
        ensure_diversity: bool
    ) -> List[Union[Movie, Anime]]:
        """Select diverse content using embedding-based clustering."""
        if not self.is_model_ready:
            return content_pool[:limit]

        # Compute all embeddings
        embeddings = []
        valid_content = []
        
        for content in content_pool:
            emb = self._get_embedding(content)
            if emb is not None:
                embeddings.append(emb)
                valid_content.append(content)
                
        if not valid_content:
            return content_pool[:limit]

        # Start with highest-rated content
        # Sort valid_content by rating
        sorted_indices = sorted(range(len(valid_content)), key=lambda i: valid_content[i].rating, reverse=True)
        
        selected = []
        selected_embeddings = []
        
        # Helper to add content
        def add_content(idx):
            selected.append(valid_content[idx])
            selected_embeddings.append(embeddings[idx])
        
        # Ensure type diversity if requested
        if ensure_diversity and limit >= 2:
            # Find best movie
            for i in sorted_indices:
                if valid_content[i].type == "movie":
                    add_content(i)
                    break
            
            # Find best anime
            for i in sorted_indices:
                if valid_content[i].type == "anime":
                    # Check if we already added a movie (to avoid duplicates if same item somehow)
                    if not selected or valid_content[i].id != selected[0].id:
                        add_content(i)
                        break
        
        # Fill remaining slots with diverse content
        for i in sorted_indices:
            if len(selected) >= limit:
                break
            
            content = valid_content[i]
            if content in selected:
                continue
            
            # If no selections yet, add the first one
            if not selected_embeddings:
                add_content(i)
                continue
            
            # Check diversity
            content_emb = embeddings[i]
            
            # Compute minimum similarity to already selected items
            similarities = [
                np.dot(content_emb, sel_emb) / (np.linalg.norm(content_emb) * np.linalg.norm(sel_emb))
                for sel_emb in selected_embeddings
            ]
            min_similarity = min(similarities) if similarities else 0
            
            # Add if sufficiently diverse (similarity < 0.85)
            if min_similarity < 0.85 or len(selected) < limit:
                add_content(i)
        
        return selected
    
    def get_personalized_recommendations(
        self,
        all_content: List[Union[Movie, Anime]],
        user_taste_embedding: Optional[np.ndarray] = None,
        mood: Optional[str] = None,
        limit: int = 6,
        ensure_diversity: bool = True,
        interaction_count: int = 0,
        favorite_genres: Optional[List[str]] = None,
        favorite_moods: Optional[List[str]] = None
    ) -> List[Tuple[Union[Movie, Anime], float, bool]]:
        """
        Get personalized recommendations based on multi-factor AI scoring.
        """
        from services.taste_reasoning import taste_reasoning
        from datetime import datetime
        
        # 1. Do not hard-filter by mood anymore. Keep all content in pool.
        content_pool = all_content
        if not content_pool:
            return []
        
        if not self.is_model_ready or user_taste_embedding is None:
            regular_recs = self.get_recommendations(all_content, mood, limit, ensure_diversity)
            return [(content, 0.5, False) for content in regular_recs]
        
        confidence = taste_reasoning.compute_taste_confidence(interaction_count)
        random_seed = (interaction_count % 100) / 100.0
        is_exploring = taste_reasoning.should_explore(confidence, interaction_count, random_seed)
        
        current_year = datetime.utcnow().year
        scored_content = []
        
        for content in content_pool:
            content_emb = self._get_embedding(content)
            if content_emb is None:
                continue
            
            # Factor 1: Semantic Taste Similarity
            taste_similarity = np.dot(user_taste_embedding, content_emb) / (
                np.linalg.norm(user_taste_embedding) * np.linalg.norm(content_emb)
            )
            
            # Factor 2: Non-linear Rating Boost
            rating_boost = taste_reasoning.compute_rating_boost(content.rating)
            
            # Extract top genres and moods for scoring if they are dicts (EMA)
            fav_genres_list = list(favorite_genres.keys())[:5] if isinstance(favorite_genres, dict) else favorite_genres
            fav_moods_list = list(favorite_moods.keys())[:3] if isinstance(favorite_moods, dict) else favorite_moods

            # 3. Mood match (0.10 weight)
            mood_match = taste_reasoning.compute_mood_match_score(
                content.mood,
                mood,
                fav_moods_list
            )
            
            # 4. Popularity Score
            popularity_score = taste_reasoning.compute_popularity_score(content.popularity)
            
            # 5. Recency Score
            recency_score = taste_reasoning.compute_recency_score(
                content.year, current_year, settings.recency_decay_lambda
            )
            
            # 6. Exploration bonus (0.05 weight)
            exploration_bonus = 0.0
            is_exploration_item = False
            if is_exploring and fav_genres_list:
                exploration_bonus = taste_reasoning.compute_exploration_bonus(
                    content.genres, fav_genres_list, is_exploring
                )
                if exploration_bonus > 0:
                    is_exploration_item = True
            
            # Final Score Equation
            base_score = (
                (taste_similarity * settings.weight_semantic_taste) +
                (rating_boost * settings.weight_rating) +
                (mood_match * settings.weight_mood) +
                (popularity_score * settings.weight_popularity) +
                (recency_score * 0.05) + # small baked recency weight
                (exploration_bonus * settings.weight_exploration)
            )
            
            scored_content.append((content, float(base_score), is_exploration_item))
        
        # Sort initially by base score
        scored_content.sort(key=lambda x: x[1], reverse=True)
        
        # Apply Soft Diversity Penalty
        if ensure_diversity:
            selected = []
            selected_embeddings = []
            
            movies = [(c, s, e) for c, s, e in scored_content if c.type == "movie"]
            anime = [(c, s, e) for c, s, e in scored_content if c.type == "anime"]
            
            if movies and len(selected) < limit:
                selected.append(movies[0])
                if self.is_model_ready:
                     selected_embeddings.append(self._get_embedding(movies[0][0]))
            
            if anime and len(selected) < limit:
                selected.append(anime[0])
                if self.is_model_ready:
                    selected_embeddings.append(self._get_embedding(anime[0][0]))
            
            for content, score, is_exploration_item in scored_content:
                if len(selected) >= limit:
                    break
                
                if any(content.id == s[0].id for s in selected):
                    continue
                
                if not self.is_model_ready or not selected_embeddings:
                    selected.append((content, score, is_exploration_item))
                    if self.is_model_ready:
                        selected_embeddings.append(self._get_embedding(content))
                    continue
                
                content_emb = self._get_embedding(content)
                similarities = [
                    np.dot(content_emb, sel_emb) / (np.linalg.norm(content_emb) * np.linalg.norm(sel_emb))
                    for sel_emb in selected_embeddings
                ]
                max_similarity = max(similarities) if similarities else 0
                
                # Apply penalty directly to the score
                penalty = taste_reasoning.compute_diversity_penalty(
                    max_similarity, penalty_strength=settings.diversity_penalty_strength
                )
                
                penalized_score = score * (1.0 - penalty)
                
                selected.append((content, penalized_score, is_exploration_item))
                selected_embeddings.append(content_emb)
                
                # Re-sort incrementally after penalty applied
                selected.sort(key=lambda x: x[1], reverse=True)
            
            return selected[:limit]
        else:
            return scored_content[:limit]



# Singleton instance
recommendation_service = RecommendationService()
