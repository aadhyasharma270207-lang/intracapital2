from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class DiscoverOpportunitiesRequest(BaseModel):
    company_name: Optional[str] = "Intracapital Corp"


class OpportunityResponse(BaseModel):
    opportunity_id: str
    name: str
    score: float
    market_potential: float
    feasibility: float
    strategic_fit: float
    asset_reusability: float
    confidence: float
    problem: str
    solution: str
    target_customers: List[str] = []
    target_industries: List[str] = []
    business_model: Optional[str] = None
    revenue_model: Optional[str] = None
    reused_assets: List[str] = []
    implementation_plan: List[str] = []
    risks: List[str] = []
    evidence: List[Any] = []
    reasoning: Optional[str] = None


class DiscoverOpportunitiesResponse(BaseModel):
    analysis_id: str
    company_name: str
    opportunities_discovered: int
    opportunities: List[OpportunityResponse]


class ExplainOpportunityResponse(BaseModel):
    opportunity_id: str
    name: str
    score: float
    explanation: str
    cited_assets: List[str]
    graph_relationships: List[Dict[str, Any]]
    score_breakdown: Dict[str, float]
