from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.schemas.schemas import SystemStatusResponse, ServiceStatus
from app.services.ollama_service import OllamaService
from app.services.qdrant_service import QdrantService
from app.services.graph_service import GraphService
from app.db.sqlite import get_db

router = APIRouter()

@router.get("/system/status", response_model=SystemStatusResponse, tags=["System"])
def get_system_status(db: Session = Depends(get_db)):
    """
    Returns live connectivity status of all core architecture modules.
    Does not spoof statuses and provides real network diagnostics.
    """
    # 1. FastAPI Check
    fastapi_status = ServiceStatus(status="ONLINE", message="FastAPI Gateway is operational.")
    
    # 2. SQLite Database Check
    sqlite_status = ServiceStatus(status="ONLINE", message="SQLite database file loaded.")
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        sqlite_status = ServiceStatus(status="OFFLINE", message=f"SQLite database error: {str(e)}")

    # 3. Ollama Status Check
    ollama_info = OllamaService.check_status()
    ollama_status = ServiceStatus(
        status=ollama_info["status"],
        message=ollama_info["message"],
        details=ollama_info.get("details")
    )

    # 4. Qdrant Status Check
    qdrant_info = QdrantService.check_status()
    qdrant_status = ServiceStatus(
        status=qdrant_info["status"],
        message=qdrant_info["message"],
        details=qdrant_info.get("details")
    )

    # 5. Neo4j Status Check
    neo4j_info = GraphService.check_status()
    neo4j_status = ServiceStatus(
        status=neo4j_info["status"],
        message=neo4j_info["message"],
        details=neo4j_info.get("details")
    )

    # 6. LangGraph status check
    # Check if langgraph is installed or fallback sequencer is used
    try:
        import langgraph
        langgraph_status = ServiceStatus(status="ONLINE", message="LangGraph module imported successfully.")
    except ImportError:
        langgraph_status = ServiceStatus(
            status="DEGRADED", 
            message="LangGraph not installed. Sequential workflow engine is executing as fallback."
        )

    return SystemStatusResponse(
        fastapi=fastapi_status,
        ollama=ollama_status,
        qdrant=qdrant_status,
        neo4j=neo4j_status,
        sqlite=sqlite_status,
        langgraph=langgraph_status
    )
