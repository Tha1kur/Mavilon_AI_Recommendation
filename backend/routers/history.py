"""
Watch history and favorites API endpoints.
Handles marking content as watched and managing favorites.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from database import get_db
from services.user_service import user_service
from models.user import WatchHistory, Favorite
from models.content import Movie, Anime

router = APIRouter()


class MarkWatchedRequest(BaseModel):
    """Request to mark content as watched."""
    content_id: str
    content_type: str  # 'movie' or 'anime'
    completion_percentage: int = 100


class AddFavoriteRequest(BaseModel):
    """Request to add content to favorites."""
    content_id: str
    content_type: str  # 'movie' or 'anime'


class WatchHistoryResponse(BaseModel):
    """Watch history item response."""
    content_id: str
    content_type: str
    watched_at: datetime
    completion_percentage: int


class FavoriteResponse(BaseModel):
    """Favorite item response."""
    content_id: str
    content_type: str
    added_at: datetime


@router.post("/{session_id}/watch")
async def mark_as_watched(
    session_id: str,
    request: MarkWatchedRequest,
    db: Session = Depends(get_db)
):
    """Mark content as watched."""
    try:
        user = user_service.get_or_create_user(db, session_id)
        
        # Check if already watched
        existing = db.query(WatchHistory).filter(
            WatchHistory.user_id == user.id,
            WatchHistory.content_id == request.content_id
        ).first()
        
        if existing:
            # Update existing record
            existing.watched_at = datetime.utcnow()
            existing.completion_percentage = request.completion_percentage
        else:
            # Create new record
            watch_entry = WatchHistory(
                user_id=user.id,
                content_id=request.content_id,
                content_type=request.content_type,
                completion_percentage=request.completion_percentage
            )
            db.add(watch_entry)
        
        db.commit()
        
        # Update taste profile (async in background)
        await user_service._update_taste_profile(db, user.id)
        
        return {
            "success": True,
            "message": "Content marked as watched"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to mark as watched: {str(e)}")


@router.post("/{session_id}/favorite")
async def add_to_favorites(
    session_id: str,
    request: AddFavoriteRequest,
    db: Session = Depends(get_db)
):
    """Add content to favorites."""
    try:
        user = user_service.get_or_create_user(db, session_id)
        
        # Check if already favorited
        existing = db.query(Favorite).filter(
            Favorite.user_id == user.id,
            Favorite.content_id == request.content_id
        ).first()
        
        if existing:
            return {
                "success": True,
                "message": "Content already in favorites",
                "already_exists": True
            }
        
        # Create new favorite
        favorite = Favorite(
            user_id=user.id,
            content_id=request.content_id,
            content_type=request.content_type
        )
        db.add(favorite)
        db.commit()
        
        # Update taste profile
        await user_service._update_taste_profile(db, user.id)
        
        return {
            "success": True,
            "message": "Content added to favorites",
            "already_exists": False
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add to favorites: {str(e)}")


@router.delete("/{session_id}/favorite/{content_id}")
async def remove_from_favorites(
    session_id: str,
    content_id: str,
    db: Session = Depends(get_db)
):
    """Remove content from favorites."""
    try:
        user = user_service.get_or_create_user(db, session_id)
        
        favorite = db.query(Favorite).filter(
            Favorite.user_id == user.id,
            Favorite.content_id == content_id
        ).first()
        
        if not favorite:
            raise HTTPException(status_code=404, detail="Favorite not found")
        
        db.delete(favorite)
        db.commit()
        
        return {
            "success": True,
            "message": "Content removed from favorites"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove favorite: {str(e)}")


@router.get("/{session_id}/history", response_model=List[WatchHistoryResponse])
async def get_watch_history(
    session_id: str,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get user's watch history."""
    try:
        user = user_service.get_or_create_user(db, session_id)
        
        history = db.query(WatchHistory).filter(
            WatchHistory.user_id == user.id
        ).order_by(WatchHistory.watched_at.desc()).limit(limit).all()
        
        return [
            WatchHistoryResponse(
                content_id=item.content_id,
                content_type=item.content_type,
                watched_at=item.watched_at,
                completion_percentage=item.completion_percentage
            )
            for item in history
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get watch history: {str(e)}")


@router.delete("/{session_id}/history/{content_id}")
async def remove_from_history(
    session_id: str,
    content_id: str,
    db: Session = Depends(get_db)
):
    """Remove content from watch history and triggers profile recalibration."""
    try:
        user = user_service.get_or_create_user(db, session_id)
        
        history_item = db.query(WatchHistory).filter(
            WatchHistory.user_id == user.id,
            WatchHistory.content_id == content_id
        ).first()
        
        if not history_item:
            raise HTTPException(status_code=404, detail="History not found")
            
        db.delete(history_item)
        
        # Also clean up related Interaction if any
        from models.user import Interaction
        interactions = db.query(Interaction).filter(
            Interaction.user_id == user.id,
            Interaction.content_id == content_id
        ).all()
        for i in interactions:
            db.delete(i)
            
        db.commit()
        
        # Recalculate profile
        await user_service.recalculate_taste_profile(db, user.id)
        
        return {
            "success": True,
            "message": "Content removed from history"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove history: {str(e)}")


@router.get("/{session_id}/favorites", response_model=List[FavoriteResponse])
async def get_favorites(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Get user's favorites."""
    try:
        user = user_service.get_or_create_user(db, session_id)
        
        favorites = db.query(Favorite).filter(
            Favorite.user_id == user.id
        ).order_by(Favorite.added_at.desc()).all()
        
        return [
            FavoriteResponse(
                content_id=item.content_id,
                content_type=item.content_type,
                added_at=item.added_at
            )
            for item in favorites
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get favorites: {str(e)}")
