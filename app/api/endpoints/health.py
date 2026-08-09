from fastapi import APIRouter
from app.schemas.health import HealthResponse
from app.services.granite_service import granite_service
from app.services.neo4j_service import neo4j_service
from app.services.qdrant_service import qdrant_service

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def get_health():
    ollama_status = "ok" if granite_service.is_available() else "offline"
    neo4j_status = "ok" if neo4j_service.is_connected else "fallback_local"
    qdrant_status = "ok" if qdrant_service.is_connected else "fallback_local"

    return HealthResponse(
        api="ok",
        ollama=ollama_status,
        neo4j=neo4j_status,
        qdrant=qdrant_status
    )
