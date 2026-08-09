from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Text, Float, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.sqlite import Base

def get_utc_now():
    return datetime.now(timezone.utc)


def generate_uuid():
    return str(uuid.uuid4())

class Company(Base):
    __tablename__ = "companies"
    
    id = Column(String(36), default=generate_uuid, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=get_utc_now)
    
    assets = relationship("Asset", back_populates="company", cascade="all, delete-orphan")
    opportunities = relationship("Opportunity", back_populates="company", cascade="all, delete-orphan")

class Asset(Base):
    __tablename__ = "assets"
    
    id = Column(String(36), default=generate_uuid, primary_key=True)
    company_id = Column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    file_name = Column(String(255), nullable=False)
    asset_type = Column(String(50), nullable=False)
    department = Column(String(100), nullable=True)
    source = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=get_utc_now)
    metadata_json = Column(JSON, nullable=True)
    content = Column(Text, nullable=True)
    status = Column(String(50), default="pending")  # pending, processing, processed, failed
    
    company = relationship("Company", back_populates="assets")
    chunks = relationship("AssetChunk", back_populates="asset", cascade="all, delete-orphan")
    evidences = relationship("OpportunityEvidence", back_populates="asset", cascade="all, delete-orphan")

class AssetChunk(Base):
    __tablename__ = "asset_chunks"
    
    id = Column(String(36), default=generate_uuid, primary_key=True)
    asset_id = Column(String(36), ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    text = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    metadata_json = Column(JSON, nullable=True)
    
    asset = relationship("Asset", back_populates="chunks")
    evidences = relationship("OpportunityEvidence", back_populates="chunk", cascade="all, delete-orphan")

class Opportunity(Base):
    __tablename__ = "opportunities"
    
    id = Column(String(36), default=generate_uuid, primary_key=True)
    company_id = Column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    short_description = Column(Text, nullable=False)
    problem = Column(Text, nullable=False)
    solution = Column(Text, nullable=False)
    target_customers = Column(Text, nullable=False)
    industry = Column(String(100), nullable=False)
    business_model = Column(String(100), nullable=False)
    revenue_model = Column(String(100), nullable=False)
    
    # Raw criteria scores
    market_potential = Column(Float, nullable=False, default=0.0)
    feasibility = Column(Float, nullable=False, default=0.0)
    strategic_fit = Column(Float, nullable=False, default=0.0)
    asset_reusability = Column(Float, nullable=False, default=0.0)
    confidence = Column(Float, nullable=False, default=0.0)
    overall_score = Column(Float, nullable=False, default=0.0)
    
    required_resources = Column(Text, nullable=True)
    existing_assets_used = Column(Text, nullable=True)
    key_activities = Column(Text, nullable=True)
    key_resources = Column(Text, nullable=True)
    cost_drivers = Column(Text, nullable=True)
    go_to_market = Column(Text, nullable=True)
    risks = Column(Text, nullable=True)
    assumptions = Column(Text, nullable=True)
    reasoning = Column(Text, nullable=True)
    status = Column(String(50), default="pending")  # pending, approved, rejected, saved
    created_at = Column(DateTime, default=get_utc_now)
    
    company = relationship("Company", back_populates="opportunities")
    evidence = relationship("OpportunityEvidence", back_populates="opportunity", cascade="all, delete-orphan")
    business_model_canvas = relationship("BusinessModel", back_populates="opportunity", uselist=False, cascade="all, delete-orphan")
    validation_results = relationship("ValidationResult", back_populates="opportunity", cascade="all, delete-orphan")

class OpportunityEvidence(Base):
    __tablename__ = "opportunity_evidence"
    
    id = Column(String(36), default=generate_uuid, primary_key=True)
    opportunity_id = Column(String(36), ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False)
    chunk_id = Column(String(36), ForeignKey("asset_chunks.id", ondelete="CASCADE"), nullable=False)
    asset_id = Column(String(36), ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    relevance_score = Column(Float, nullable=False, default=1.0)
    supporting_text = Column(Text, nullable=False)
    
    opportunity = relationship("Opportunity", back_populates="evidence")
    chunk = relationship("AssetChunk", back_populates="evidences")
    asset = relationship("Asset", back_populates="evidences")

class BusinessModel(Base):
    __tablename__ = "business_models"
    
    id = Column(String(36), default=generate_uuid, primary_key=True)
    opportunity_id = Column(String(36), ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False, unique=True)
    customer_segments = Column(Text, nullable=False)
    value_propositions = Column(Text, nullable=False)
    channels = Column(Text, nullable=False)
    customer_relationships = Column(Text, nullable=False)
    revenue_streams = Column(Text, nullable=False)
    key_resources = Column(Text, nullable=False)
    key_activities = Column(Text, nullable=False)
    key_partners = Column(Text, nullable=False)
    cost_structure = Column(Text, nullable=False)
    first_validation = Column(Text, nullable=False)
    
    opportunity = relationship("Opportunity", back_populates="business_model_canvas")

class ValidationResult(Base):
    __tablename__ = "validation_results"
    
    id = Column(String(36), default=generate_uuid, primary_key=True)
    opportunity_id = Column(String(36), ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False)
    market_potential = Column(Float, nullable=False)
    feasibility = Column(Float, nullable=False)
    strategic_fit = Column(Float, nullable=False)
    asset_reusability = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    overall_score = Column(Float, nullable=False)
    adjusted_by = Column(String(100), default="Human User")
    comments = Column(Text, nullable=True)
    status = Column(String(50), default="pending")  # Approved, Rejected, Under Review
    created_at = Column(DateTime, default=get_utc_now)
    
    opportunity = relationship("Opportunity", back_populates="validation_results")

class ProcessingJob(Base):
    __tablename__ = "processing_jobs"
    
    id = Column(String(36), default=generate_uuid, primary_key=True)
    company_id = Column(String(36), nullable=False)
    job_type = Column(String(50), nullable=False)  # ingestion, discovery
    status = Column(String(50), default="running")  # running, completed, failed
    current_step = Column(String(100), nullable=True)
    progress = Column(Float, default=0.0)
    elapsed_time = Column(Float, default=0.0)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)
