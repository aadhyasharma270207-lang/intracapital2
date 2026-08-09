from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime

# --- COMPANY SCHEMAS ---
class CompanyBase(BaseModel):
    name: str
    description: Optional[str] = None

class CompanyCreate(CompanyBase):
    pass

class CompanyResponse(CompanyBase):
    id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# --- ASSET SCHEMAS ---
class AssetResponse(BaseModel):
    id: str
    company_id: str
    file_name: str
    asset_type: str
    department: Optional[str] = None
    source: Optional[str] = None
    created_at: datetime
    status: str
    metadata_json: Optional[Dict[str, Any]] = None
    relationships_count: int = 0
    chunks_count: int = 0

    model_config = ConfigDict(from_attributes=True)

class AssetDetailResponse(AssetResponse):
    content: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

# --- BUSINESS MODEL CANVAS SCHEMAS ---
class BusinessModelCanvasResponse(BaseModel):
    id: str
    opportunity_id: str
    customer_segments: str
    value_propositions: str
    channels: str
    customer_relationships: str
    revenue_streams: str
    key_resources: str
    key_activities: str
    key_partners: str
    cost_structure: str
    first_validation: str

    model_config = ConfigDict(from_attributes=True)

# --- EVIDENCE SCHEMAS ---
class OpportunityEvidenceResponse(BaseModel):
    id: str
    opportunity_id: str
    chunk_id: str
    asset_id: str
    file_name: str
    asset_type: str
    relevance_score: float
    supporting_text: str

    model_config = ConfigDict(from_attributes=True)

# --- VALIDATION SCHEMAS ---
class ValidationRequest(BaseModel):
    market_potential: float = Field(..., ge=0, le=100)
    feasibility: float = Field(..., ge=0, le=100)
    strategic_fit: float = Field(..., ge=0, le=100)
    asset_reusability: float = Field(..., ge=0, le=100)
    confidence: float = Field(..., ge=0, le=100)
    comments: Optional[str] = None
    status: str = "pending" # Approved, Rejected, Under Review

class ValidationResponse(BaseModel):
    id: str
    opportunity_id: str
    market_potential: float
    feasibility: float
    strategic_fit: float
    asset_reusability: float
    confidence: float
    overall_score: float
    adjusted_by: str
    comments: Optional[str] = None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# --- OPPORTUNITY SCHEMAS ---
class OpportunityResponse(BaseModel):
    id: str
    company_id: str
    title: str
    short_description: str
    overall_score: float
    market_potential: float
    feasibility: float
    strategic_fit: float
    asset_reusability: float
    confidence: float
    industry: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class OpportunityDetailResponse(OpportunityResponse):
    problem: str
    solution: str
    target_customers: str
    business_model: str
    revenue_model: str
    required_resources: Optional[str] = None
    existing_assets_used: Optional[str] = None
    key_activities: Optional[str] = None
    key_resources: Optional[str] = None
    cost_drivers: Optional[str] = None
    go_to_market: Optional[str] = None
    risks: Optional[str] = None
    assumptions: Optional[str] = None
    reasoning: Optional[str] = None
    evidence: List[OpportunityEvidenceResponse] = []
    business_model_canvas: Optional[BusinessModelCanvasResponse] = None
    validation_results: List[ValidationResponse] = []

    model_config = ConfigDict(from_attributes=True)

# --- COMPARE SCHEMAS ---
class CompareRequest(BaseModel):
    opportunity_ids: List[str]

class CompareResponse(BaseModel):
    id: str
    title: str
    overall_score: float
    market_potential: float
    feasibility: float
    strategic_fit: float
    asset_reusability: float
    confidence: float
    short_description: str
    industry: str
    business_model: str
    revenue_model: str
    required_resources: Optional[str] = None
    risks: Optional[str] = None

# --- PROCESSING JOB SCHEMAS ---
class ProcessingJobResponse(BaseModel):
    id: str
    company_id: str
    job_type: str
    status: str
    current_step: Optional[str] = None
    progress: float
    elapsed_time: float
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# --- SYSTEM SCHEMAS ---
class ServiceStatus(BaseModel):
    status: str  # ONLINE, DEGRADED, OFFLINE
    message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class SystemStatusResponse(BaseModel):
    fastapi: ServiceStatus
    ollama: ServiceStatus
    qdrant: ServiceStatus
    neo4j: ServiceStatus
    sqlite: ServiceStatus
    langgraph: ServiceStatus

# --- ANALYTICS SCHEMAS ---
class CategoryCount(BaseModel):
    name: str
    count: int

class ScoreDistribution(BaseModel):
    range: str
    count: int

class AnalyticsResponse(BaseModel):
    total_assets: int
    processed_assets: int
    failed_assets: int
    total_opportunities: int
    average_overall_score: float
    average_confidence: float
    asset_types_distribution: List[CategoryCount]
    industry_distribution: List[CategoryCount]
    opportunity_score_distribution: List[ScoreDistribution]
    asset_utilization_rate: float
    total_connections: int
