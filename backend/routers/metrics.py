"""
Metrics and monitoring endpoints.
Provides system health and performance metrics.
"""

from fastapi import APIRouter
from services.cache_service import cache_service
from database import engine
import time

router = APIRouter()

# Track request metrics
request_count = 0
start_time = time.time()


@router.get("/metrics")
async def get_metrics():
    """Get system metrics and health information."""
    global request_count
    
    # Calculate uptime
    uptime_seconds = time.time() - start_time
    uptime_hours = uptime_seconds / 3600
    
    # Get cache stats
    cache_stats = cache_service.get_stats()
    
    # Calculate cache hit rate (simplified)
    cache_hit_rate = 0.0
    if cache_stats["total_keys"] > 0:
        cache_hit_rate = (cache_stats["active_keys"] / cache_stats["total_keys"]) * 100
    
    # Database connection status
    try:
        with engine.connect() as conn:
            db_status = "healthy"
    except Exception:
        db_status = "unhealthy"
    
    return {
        "status": "healthy",
        "uptime_hours": round(uptime_hours, 2),
        "total_requests": request_count,
        "cache": {
            "total_keys": cache_stats["total_keys"],
            "active_keys": cache_stats["active_keys"],
            "expired_keys": cache_stats["expired_keys"],
            "hit_rate_percent": round(cache_hit_rate, 2)
        },
        "database": {
            "status": db_status
        }
    }


def increment_request_count():
    """Increment global request counter."""
    global request_count
    request_count += 1
