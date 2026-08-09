from fastapi import APIRouter
from app.schemas.search import SearchRequest, SearchResponse, SearchResultItem
from app.services.qdrant_service import qdrant_service

router = APIRouter()


@router.post("/search", response_model=SearchResponse)
def search_enterprise_knowledge(req: SearchRequest):
    results = qdrant_service.search(
        query=req.query,
        top_k=req.top_k or 5,
        asset_type_filter=req.asset_type,
        company_filter=req.company_name
    )

    items = [
        SearchResultItem(
            score=r.get("score", 0.0),
            content=r.get("content", ""),
            source_file=r.get("source_file"),
            asset_type=r.get("asset_type"),
            company=r.get("company"),
            page_number=r.get("page_number"),
            section_title=r.get("section_title")
        ) for r in results
    ]

    return SearchResponse(query=req.query, results=items)
