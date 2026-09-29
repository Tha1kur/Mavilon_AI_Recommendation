"""
User data models for personalization.
Tracks users, interactions, and taste profiles.
"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from database import Base


class InteractionType(str, enum.Enum):
    """Types of user interactions."""
    VIEW = "view"
    CLICK = "click"
    SEARCH = "search"


class User(Base):
    """User profile with session-based identity."""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    interactions = relationship("Interaction", back_populates="user", cascade="all, delete-orphan")
    taste_profile = relationship("TasteProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")


class Interaction(Base):
    """User interaction with content."""
    __tablename__ = "interactions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    content_id = Column(String, nullable=False)
    content_type = Column(String, nullable=False)  # 'movie' or 'anime'
    interaction_type = Column(SQLEnum(InteractionType), nullable=False)
    mood = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationship
    user = relationship("User", back_populates="interactions")


class WatchHistory(Base):
    """User watch history for content."""
    __tablename__ = "watch_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    content_id = Column(String, nullable=False)
    content_type = Column(String, nullable=False)  # 'movie' or 'anime'
    watched_at = Column(DateTime, default=datetime.utcnow, index=True)
    completion_percentage = Column(Integer, default=100)  # 0-100
    
    # Relationship
    user = relationship("User", backref="watch_history")


class Favorite(Base):
    """User favorite content."""
    __tablename__ = "favorites"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    content_id = Column(String, nullable=False)
    content_type = Column(String, nullable=False)  # 'movie' or 'anime'
    added_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationship
    user = relationship("User", backref="favorites")
    
    # Unique constraint: user can only favorite a content once
    __table_args__ = (
        UniqueConstraint('user_id', 'content_id', name='unique_user_favorite'),
    )


class TasteProfile(Base):
    """User taste profile with embeddings and preferences."""
    __tablename__ = "taste_profiles"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id"), unique=True, nullable=False)
    taste_embedding = Column(JSON, nullable=True)  # Stored as JSON array
    favorite_genres = Column(JSON, nullable=True)  # List of genres
    favorite_moods = Column(JSON, nullable=True)  # List of moods
    interaction_count = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = relationship("User", back_populates="taste_profile")
