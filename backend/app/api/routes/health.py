from fastapi import APIRouter
from datetime import datetime, timezone

router = APIRouter()

@router.get("/health", tags=["Health"])
def get_health():
    """
    Returns basic API status check.
    """
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
