from fastapi import APIRouter
from app.api.endpoints import health, documents, assets, graph, search, opportunities, analysis

api_router = APIRouter()

# Health check at top-level /health as required
api_router.include_router(health.router, tags=["Health"])

# /api/v1 prefix routes
v1_router = APIRouter(prefix="/api/v1")
v1_router.include_router(documents.router, tags=["Documents"])
v1_router.include_router(assets.router, tags=["Assets"])
v1_router.include_router(graph.router, tags=["Knowledge Graph"])
v1_router.include_router(search.router, tags=["Vector Search"])
v1_router.include_router(opportunities.router, tags=["Opportunities"])
v1_router.include_router(analysis.router, tags=["Analysis Runs"])

api_router.include_router(v1_router)
