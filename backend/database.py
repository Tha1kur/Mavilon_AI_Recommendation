"""
Database configuration and session management.
SQLite database for user profiles and interactions.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import get_settings

settings = get_settings()

# SQLite database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./mavilon_users.db"

# Create engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # Needed for SQLite
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables and run basic migrations."""
    Base.metadata.create_all(bind=engine)
    
    # Simple SQLite migration for new columns in TasteProfile
    import sqlite3
    import os
    
    db_path = "./mavilon_users.db"
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='taste_profiles'")
        if cursor.fetchone():
            cursor.execute("PRAGMA table_info(taste_profiles)")
            columns = [info[1] for info in cursor.fetchall()]
            
            if "interaction_count" not in columns:
                cursor.execute("ALTER TABLE taste_profiles ADD COLUMN interaction_count INTEGER DEFAULT 0")
                
            if "updated_at" not in columns:
                cursor.execute("ALTER TABLE taste_profiles ADD COLUMN updated_at DATETIME")
                
        conn.commit()
        conn.close()
