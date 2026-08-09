from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class OpportunityModel(BaseModel):
    name: str = Field(..., description="The name of the discovered business venture opportunity")
    pitch: str = Field(..., description="One-line pitch summarizing the business model")
    problem: str = Field(..., description="Operational problem grounded in the company's files")
    solution: str = Field(..., description="Proprietary solution leveraging internal assets")
    existing_assets: List[str] = Field(..., description="Names of specific patents, reports, or logs used")
    asset_connection: str = Field(..., description="How the assets connect together to form this opportunity")
    target_customers: List[str] = Field(..., description="Customer segments or industries to target")
    revenue_model: str = Field(..., description="Description of the monetization model")
    market_potential: float = Field(..., ge=0, le=100, description="Potential score out of 100")
    feasibility: float = Field(..., ge=0, le=100, description="Technical feasibility score out of 100")
    strategic_fit: float = Field(..., ge=0, le=100, description="Strategic fit score out of 100")
    asset_reusability: float = Field(..., ge=0, le=100, description="Asset reusability score out of 100")
    confidence: float = Field(..., ge=0, le=100, description="Inference engine confidence rating out of 100")
    evidence: List[str] = Field(..., description="Direct references to files/lines backing the opportunity")
    reasoning: str = Field(..., description="Concise explanation of the commercial opportunity")
    
    # Optional fields populated in scoring step or advanced generation
    overall_score: Optional[float] = None
    score_explanation: Optional[str] = None
    id: Optional[str] = None
    implementation_difficulty: Optional[str] = "Medium"
    expected_business_impact: Optional[str] = "High Strategic Growth"
    key_risks: Optional[List[str]] = Field(default_factory=list)
    recommended_next_experiment: Optional[str] = "Market feasibility pilot study"

class OpportunityListResponse(BaseModel):
    status: str
    opportunities: List[OpportunityModel]

class ValidationRequest(BaseModel):
    opportunity_id: str
    market_potential: float
    feasibility: float
    strategic_fit: float
    asset_reusability: float
    confidence: float

class ValidationResponse(BaseModel):
    opportunity_id: str
    original_score: float
    adjusted_score: float
    difference: float
    score_explanation: str

class BusinessModelRequest(BaseModel):
    opportunity_id: str

class BusinessModelResponse(BaseModel):
    opportunity_id: str
    target_customer: str
    value_proposition: str
    revenue_model: str
    distribution: str
    key_resources: str
    key_activities: str
    cost_drivers: str
    go_to_market: str
    first_validation_experiment: str
    labels: Dict[str, str]

class HealthCheckResponse(BaseModel):
    fastapi: str
    rag: str
    chromadb: str
    granite: str

class IngestionMetrics(BaseModel):
    documents_processed: int
    chunks: int
    opportunities: int
    average_confidence: float
    top_score: float
    processing_time: float
