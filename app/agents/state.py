from typing import List, Dict, Any, TypedDict, Optional


class DiscoveryState(TypedDict):
    company_id: str
    company_name: str
    enterprise_assets: List[Dict[str, Any]]
    rag_evidence: List[Dict[str, Any]]
    graph_context: Dict[str, Any]
    underutilized_assets: List[Dict[str, Any]]
    capabilities: List[str]
    market_research: Dict[str, Any]
    candidate_opportunities: List[Dict[str, Any]]
    evaluated_opportunities: List[Dict[str, Any]]
    ranked_opportunities: List[Dict[str, Any]]
    analysis_id: Optional[str]
