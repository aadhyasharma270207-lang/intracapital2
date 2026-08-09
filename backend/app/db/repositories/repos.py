from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from app.models.models import (
    Company, Asset, AssetChunk, Opportunity, 
    OpportunityEvidence, BusinessModel, ValidationResult, ProcessingJob
)

class CompanyRepository:
    @staticmethod
    def create(db: Session, name: str, description: Optional[str] = None) -> Company:
        company = Company(name=name, description=description)
        db.add(company)
        db.commit()
        db.refresh(company)
        return company

    @staticmethod
    def get_by_id(db: Session, company_id: str) -> Optional[Company]:
        return db.query(Company).filter(Company.id == company_id).first()

    @staticmethod
    def get_all(db: Session) -> List[Company]:
        return db.query(Company).all()


class AssetRepository:
    @staticmethod
    def create(db: Session, company_id: str, file_name: str, asset_type: str, 
               department: Optional[str] = None, source: Optional[str] = None,
               metadata_json: Optional[Dict[str, Any]] = None, content: Optional[str] = None) -> Asset:
        asset = Asset(
            company_id=company_id,
            file_name=file_name,
            asset_type=asset_type,
            department=department,
            source=source,
            metadata_json=metadata_json,
            content=content,
            status="pending"
        )
        db.add(asset)
        db.commit()
        db.refresh(asset)
        return asset

    @staticmethod
    def get_by_id(db: Session, asset_id: str) -> Optional[Asset]:
        return db.query(Asset).filter(Asset.id == asset_id).first()

    @staticmethod
    def get_all(db: Session) -> List[Asset]:
        return db.query(Asset).all()

    @staticmethod
    def get_by_company(db: Session, company_id: str) -> List[Asset]:
        return db.query(Asset).filter(Asset.company_id == company_id).all()

    @staticmethod
    def update_status(db: Session, asset_id: str, status: str, content: Optional[str] = None) -> Optional[Asset]:
        asset = db.query(Asset).filter(Asset.id == asset_id).first()
        if asset:
            asset.status = status
            if content is not None:
                asset.content = content
            db.commit()
            db.refresh(asset)
        return asset

    @staticmethod
    def delete(db: Session, asset_id: str) -> bool:
        asset = db.query(Asset).filter(Asset.id == asset_id).first()
        if asset:
            db.delete(asset)
            db.commit()
            return True
        return False

    @staticmethod
    def create_chunk(db: Session, asset_id: str, text: str, chunk_index: int, 
                     metadata_json: Optional[Dict[str, Any]] = None) -> AssetChunk:
        chunk = AssetChunk(
            asset_id=asset_id,
            text=text,
            chunk_index=chunk_index,
            metadata_json=metadata_json
        )
        db.add(chunk)
        db.commit()
        db.refresh(chunk)
        return chunk

    @staticmethod
    def get_chunks_by_asset(db: Session, asset_id: str) -> List[AssetChunk]:
        return db.query(AssetChunk).filter(AssetChunk.asset_id == asset_id).order_by(AssetChunk.chunk_index).all()


class OpportunityRepository:
    @staticmethod
    def create(db: Session, company_id: str, title: str, short_description: str, problem: str,
               solution: str, target_customers: str, industry: str, business_model: str,
               revenue_model: str, market_potential: float, feasibility: float,
               strategic_fit: float, asset_reusability: float, confidence: float,
               overall_score: float, required_resources: Optional[str] = None,
               existing_assets_used: Optional[str] = None, key_activities: Optional[str] = None,
               key_resources: Optional[str] = None, cost_drivers: Optional[str] = None,
               go_to_market: Optional[str] = None, risks: Optional[str] = None,
               assumptions: Optional[str] = None, reasoning: Optional[str] = None) -> Opportunity:
        opp = Opportunity(
            company_id=company_id,
            title=title,
            short_description=short_description,
            problem=problem,
            solution=solution,
            target_customers=target_customers,
            industry=industry,
            business_model=business_model,
            revenue_model=revenue_model,
            market_potential=market_potential,
            feasibility=feasibility,
            strategic_fit=strategic_fit,
            asset_reusability=asset_reusability,
            confidence=confidence,
            overall_score=overall_score,
            required_resources=required_resources,
            existing_assets_used=existing_assets_used,
            key_activities=key_activities,
            key_resources=key_resources,
            cost_drivers=cost_drivers,
            go_to_market=go_to_market,
            risks=risks,
            assumptions=assumptions,
            reasoning=reasoning,
            status="pending"
        )
        db.add(opp)
        db.commit()
        db.refresh(opp)
        return opp

    @staticmethod
    def get_by_id(db: Session, opp_id: str) -> Optional[Opportunity]:
        return db.query(Opportunity).filter(Opportunity.id == opp_id).first()

    @staticmethod
    def get_all(db: Session) -> List[Opportunity]:
        return db.query(Opportunity).all()

    @staticmethod
    def get_by_company(db: Session, company_id: str) -> List[Opportunity]:
        return db.query(Opportunity).filter(Opportunity.company_id == company_id).all()

    @staticmethod
    def delete_by_company(db: Session, company_id: str):
        db.query(Opportunity).filter(Opportunity.company_id == company_id).delete()
        db.commit()

    @staticmethod
    def create_evidence(db: Session, opportunity_id: str, chunk_id: str, asset_id: str,
                        relevance_score: float, supporting_text: str) -> OpportunityEvidence:
        evidence = OpportunityEvidence(
            opportunity_id=opportunity_id,
            chunk_id=chunk_id,
            asset_id=asset_id,
            relevance_score=relevance_score,
            supporting_text=supporting_text
        )
        db.add(evidence)
        db.commit()
        db.refresh(evidence)
        return evidence

    @staticmethod
    def create_business_model(db: Session, opportunity_id: str, customer_segments: str,
                              value_propositions: str, channels: str, customer_relationships: str,
                              revenue_streams: str, key_resources: str, key_activities: str,
                              key_partners: str, cost_structure: str, first_validation: str) -> BusinessModel:
        bm = BusinessModel(
            opportunity_id=opportunity_id,
            customer_segments=customer_segments,
            value_propositions=value_propositions,
            channels=channels,
            customer_relationships=customer_relationships,
            revenue_streams=revenue_streams,
            key_resources=key_resources,
            key_activities=key_activities,
            key_partners=key_partners,
            cost_structure=cost_structure,
            first_validation=first_validation
        )
        db.add(bm)
        db.commit()
        db.refresh(bm)
        return bm

    @staticmethod
    def create_validation_result(db: Session, opportunity_id: str, market_potential: float,
                                 feasibility: float, strategic_fit: float, asset_reusability: float,
                                 confidence: float, overall_score: float, adjusted_by: str,
                                 comments: Optional[str] = None, status: str = "pending") -> ValidationResult:
        val = ValidationResult(
            opportunity_id=opportunity_id,
            market_potential=market_potential,
            feasibility=feasibility,
            strategic_fit=strategic_fit,
            asset_reusability=asset_reusability,
            confidence=confidence,
            overall_score=overall_score,
            adjusted_by=adjusted_by,
            comments=comments,
            status=status
        )
        db.add(val)
        
        # Update the main opportunity scores and status as well
        opp = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
        if opp:
            opp.market_potential = market_potential
            opp.feasibility = feasibility
            opp.strategic_fit = strategic_fit
            opp.asset_reusability = asset_reusability
            opp.confidence = confidence
            opp.overall_score = overall_score
            opp.status = status.lower()
            
        db.commit()
        db.refresh(val)
        return val


class ProcessingJobRepository:
    @staticmethod
    def create(db: Session, company_id: str, job_type: str, status: str = "running",
               current_step: Optional[str] = None, progress: float = 0.0) -> ProcessingJob:
        job = ProcessingJob(
            company_id=company_id,
            job_type=job_type,
            status=status,
            current_step=current_step,
            progress=progress,
            elapsed_time=0.0
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def get_by_id(db: Session, job_id: str) -> Optional[ProcessingJob]:
        return db.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()

    @staticmethod
    def update(db: Session, job_id: str, status: Optional[str] = None, 
               current_step: Optional[str] = None, progress: Optional[float] = None,
               elapsed_time: Optional[float] = None, error_message: Optional[str] = None) -> Optional[ProcessingJob]:
        job = db.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()
        if job:
            if status is not None:
                job.status = status
            if current_step is not None:
                job.current_step = current_step
            if progress is not None:
                job.progress = progress
            if elapsed_time is not None:
                job.elapsed_time = elapsed_time
            if error_message is not None:
                job.error_message = error_message
            db.commit()
            db.refresh(job)
        return job
