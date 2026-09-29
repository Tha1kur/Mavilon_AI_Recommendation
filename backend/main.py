"""
MAVILON AI Recommendation - FastAPI Backend
Main application entry point with CORS configuration.
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from dotenv import load_dotenv
load_dotenv()

from config import get_settings
from database import init_db
from utils.logger import logger
import time
import uuid

# Import routers
from routers import movies, anime, search, recommend, users, history, chat, content, metrics

settings = get_settings()

app = FastAPI(
    title="MAVILON AI Recommendation API",
    description="Production-ready AI-powered movie and anime recommendation system",
    version="4.0.0"
)

# Configure CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001"
    ],
    allow_credentials=True,
    allow_methods=["*"],   # MUST allow OPTIONS
    allow_headers=["*"],   # MUST allow all headers
)

from fastapi.responses import Response

@app.options("/{path:path}")
async def options_handler(path: str, request: Request):
    return Response(status_code=200)


# Request ID middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add unique request ID to each request."""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    # Track request
    from routers.metrics import increment_request_count
    increment_request_count()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url.path}", extra={"request_id": request_id})
    
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # Log response
    logger.info(
        f"Response: {response.status_code} - {process_time:.3f}s",
        extra={"request_id": request_id}
    )
    
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = str(process_time)
    
    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions."""
    request_id = getattr(request.state, "request_id", "unknown")
    
    logger.error(
        f"Unhandled exception: {str(exc)}",
        extra={"request_id": request_id},
        exc_info=True
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "request_id": request_id
        }
    )


# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database tables and AI models on startup."""
    init_db()
    
    # Start background model loading
    from services.recommendation_service import recommendation_service
    recommendation_service.load_model()
    
    logger.info("Database initialized successfully")
    logger.info(f"MAVILON AI API v4.0.0 started")
    
    # Log API configuration status
    if not settings.is_tmdb_configured():
        logger.warning(
            "⚠️  TMDB API key not configured! "
            "Get your free API key at: https://www.themoviedb.org/settings/api"
        )
    else:
        logger.info("✓ TMDB API configured")
    
    logger.info(f"✓ AI Model: {settings.embedding_model}")


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "online",
        "service": "MAVILON AI Recommendation API",
        "version": "4.0.0",
        "features": [
            "personalization",
            "ai_explanations",
            "taste_profiling",
            "watch_history",
            "favorites",
            "ai_chat",
            "content_details"
        ]
    }


@app.get("/health")
async def health_check():
    """Detailed health check with configuration guidance."""
    tmdb_configured = settings.is_tmdb_configured()
    
    from services.recommendation_service import recommendation_service
    
    health_data = {
        "status": "healthy",
        "version": "4.0.0",
        "configuration": {
            "tmdb_configured": tmdb_configured,
            "ai_model": settings.embedding_model,
            "ai_model_ready": recommendation_service.is_model_ready,
            "database": "sqlite",
            "personalization": "enabled",
            "caching": "enabled"
        }
    }
    
    # Add setup instructions if APIs not configured
    if not tmdb_configured:
        health_data["setup_required"] = []
        
        health_data["setup_required"].append({
            "service": "TMDB",
            "message": "TMDB API key not configured. Content endpoints will have limited functionality.",
            "action": "Get your free API key at https://www.themoviedb.org/settings/api",
            "env_var": "TMDB_API_KEY"
        })
    
    return health_data


# Include routers
app.include_router(movies.router, prefix="/api/movies", tags=["movies"])
app.include_router(anime.router, prefix="/api/anime", tags=["anime"])
app.include_router(search.router, prefix="/api", tags=["search"])
app.include_router(recommend.router, prefix="/api", tags=["recommendations"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(history.router, prefix="/api/users", tags=["history"])
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(content.router, prefix="/api", tags=["content"])
app.include_router(metrics.router, prefix="/api", tags=["metrics"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=True
    )
