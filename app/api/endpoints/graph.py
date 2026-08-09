from typing import Dict, Any
from fastapi import APIRouter
from app.services.neo4j_service import neo4j_service

router = APIRouter()


@router.get("/graph")
def get_full_graph():
    return neo4j_service.get_full_graph()


@router.get("/graph/asset/{asset_id}")
def get_asset_graph(asset_id: str):
    related = neo4j_service.find_related_assets(asset_id)
    return {
        "asset_id": asset_id,
        "relationships": related
    }
