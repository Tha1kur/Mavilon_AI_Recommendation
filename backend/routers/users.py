"""
User management API endpoints.
Handles user sessions, profiles, and interaction tracking.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict, Field, StrictStr, field_validator
from typing import Optional
from database import get_db
from services.user_service import user_service
from models.user import InteractionType, User
import uuid

router = APIRouter()


class SessionRequest(BaseModel):
    """An omitted identity creates a session; supplied identities must exist."""
    model_config = ConfigDict(extra="forbid")
    session_id: Optional[StrictStr] = Field(default=None, min_length=1)


class SessionResponse(BaseModel):
    """Response for session creation."""
    session_id: str
    user_id: str
    is_new: bool


class InteractionRequest(BaseModel):
    """Request to track user interaction."""
    content_id: str
    content_type: str  # 'movie' or 'anime'
    interaction_type: str  # 'view', 'click', 'search'
    mood: Optional[str] = None


class TasteProfileResponse(BaseModel):
    """User taste profile response."""
    favorite_genres: dict[str, float] = Field(default_factory=dict)
    favorite_moods: dict[str, float] = Field(default_factory=dict)
    interaction_count: int = 0

    @field_validator("favorite_genres", "favorite_moods", mode="before")
    @classmethod
    def normalize_stored_scores(cls, value):
        if value is None:
            return {}
        # Match the service's existing conversion of legacy unscored lists.
        if isinstance(value, list):
            return {label: 1.0 for label in value}
        return value


@router.post("/session", response_model=SessionResponse)
async def create_or_get_session(
    request: Request,
    payload: Optional[SessionRequest] = None,
    db: Session = Depends(get_db)
):
    """
    Create new user session or retrieve existing one.
    If session_id is provided, retrieve that session.
    Otherwise, create a new session.
    """
    if request.query_params:
        raise HTTPException(status_code=400, detail="Use a JSON body for session requests")
    session_id = payload.session_id if payload else None
    try:
        if session_id is None:
            # Generate new session ID
            session_id = str(uuid.uuid4())
            is_new = True
        else:
            is_new = False
            if not db.query(User).filter(User.session_id == session_id).first():
                raise HTTPException(status_code=404, detail="Session not found")
        
        user = user_service.get_or_create_user(db, session_id)
        
        return SessionResponse(
            session_id=user.session_id,
            user_id=user.id,
            is_new=is_new
        )
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create session")


@router.get("/{session_id}/profile", response_model=TasteProfileResponse)
async def get_user_profile(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Get user's taste profile."""
    try:
        user = user_service.get_or_create_user(db, session_id)
        taste_profile = user_service.get_taste_profile(db, user.id)
        
        if not taste_profile:
            return TasteProfileResponse(interaction_count=0)
        
        return TasteProfileResponse(
            favorite_genres=taste_profile.favorite_genres,
            favorite_moods=taste_profile.favorite_moods,
            interaction_count=taste_profile.interaction_count
        )
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to get profile")


@router.post("/{session_id}/interact")
async def track_interaction(
    session_id: str,
    request: InteractionRequest,
    db: Session = Depends(get_db)
):
    """Track user interaction with content."""
    try:
        # Validate interaction type
        try:
            interaction_type = InteractionType(request.interaction_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid interaction type: {request.interaction_type}")
        
        interaction = await user_service.track_interaction(
            db=db,
            session_id=session_id,
            content_id=request.content_id,
            content_type=request.content_type,
            interaction_type=interaction_type,
            mood=request.mood
        )
        
        return {
            "success": True,
            "interaction_id": interaction.id,
            "message": "Interaction tracked successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to track interaction: {str(e)}")
