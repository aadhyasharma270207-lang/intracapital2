import datetime
import uuid
from sqlalchemy import Column, String, Text, Float, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.database import Base


def generate_uuid():
    return str(uuid.uuid4())


class Company(Base):
    __tablename__ = "companies"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False, unique=True)
    industry = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    documents = relationship("Document", back_populates="company", cascade="all, delete-orphan")
    assets = relationship("Asset", back_populates="company", cascade="all, delete-orphan")
    analysis_runs = relationship("AnalysisRun", back_populates="company", cascade="all, delete-orphan")


class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_path = Column(String(512), nullable=False)
    asset_type = Column(String(50), nullable=False, default="OTHER")
    status = Column(String(50), default="processed")
    chunk_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    company = relationship("Company", back_populates="documents")
    assets = relationship("Asset", back_populates="document", cascade="all, delete-orphan")


class Asset(Base):
    __tablename__ = "assets"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False)
    document_id = Column(String(36), ForeignKey("documents.id"), nullable=True)
    name = Column(String(255), nullable=False)
    asset_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    source_file = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    company = relationship("Company", back_populates="assets")
    document = relationship("Document", back_populates="assets")
    metadata_entries = relationship("AssetMetadata", back_populates="asset", cascade="all, delete-orphan")


class AssetMetadata(Base):
    __tablename__ = "asset_metadata"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    asset_id = Column(String(36), ForeignKey("assets.id"), nullable=False)
    key = Column(String(255), nullable=False)
    value = Column(Text, nullable=False)

    asset = relationship("Asset", back_populates="metadata_entries")


class AnalysisRun(Base):
    __tablename__ = "analysis_runs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False)
    status = Column(String(50), default="completed")
    opportunities_discovered = Column(Integer, default=0)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    company = relationship("Company", back_populates="analysis_runs")
    opportunities = relationship("Opportunity", back_populates="analysis_run", cascade="all, delete-orphan")


class Opportunity(Base):
    __tablename__ = "opportunities"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    analysis_run_id = Column(String(36), ForeignKey("analysis_runs.id"), nullable=False)
    opportunity_code = Column(String(50), nullable=False)  # e.g. OPP-001
    name = Column(String(255), nullable=False)
    score = Column(Float, nullable=False, default=0.0)
    problem = Column(Text, nullable=False)
    solution = Column(Text, nullable=False)
    business_model = Column(Text, nullable=True)
    revenue_model = Column(Text, nullable=True)
    reasoning = Column(Text, nullable=True)
    target_customers = Column(JSON, default=list)
    target_industries = Column(JSON, default=list)
    reused_assets = Column(JSON, default=list)
    implementation_plan = Column(JSON, default=list)
    risks = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    analysis_run = relationship("AnalysisRun", back_populates="opportunities")
    score_details = relationship("OpportunityScore", back_populates="opportunity", uselist=False, cascade="all, delete-orphan")
    evidence_list = relationship("Evidence", back_populates="opportunity", cascade="all, delete-orphan")


class OpportunityScore(Base):
    __tablename__ = "opportunity_scores"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    opportunity_id = Column(String(36), ForeignKey("opportunities.id"), nullable=False)
    market_potential = Column(Float, nullable=False)
    feasibility = Column(Float, nullable=False)
    strategic_fit = Column(Float, nullable=False)
    asset_reusability = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    overall_score = Column(Float, nullable=False)

    opportunity = relationship("Opportunity", back_populates="score_details")


class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    opportunity_id = Column(String(36), ForeignKey("opportunities.id"), nullable=False)
    source_file = Column(String(255), nullable=False)
    content_snippet = Column(Text, nullable=False)
    asset_name = Column(String(255), nullable=True)
    relationship_type = Column(String(255), nullable=True)
    score = Column(Float, default=1.0)

    opportunity = relationship("Opportunity", back_populates="evidence_list")
