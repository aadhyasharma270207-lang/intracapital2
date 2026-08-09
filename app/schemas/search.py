from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class SearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5
    asset_type: Optional[str] = None
    company_name: Optional[str] = None


class SearchResultItem(BaseModel):
    score: float
    content: str
    source_file: Optional[str] = None
    asset_type: Optional[str] = None
    company: Optional[str] = None
    page_number: Optional[int] = None
    section_title: Optional[str] = None


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResultItem]
