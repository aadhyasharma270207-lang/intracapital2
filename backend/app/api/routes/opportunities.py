from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.schemas.schemas import (
    OpportunityResponse, OpportunityDetailResponse, 
    OpportunityEvidenceResponse, BusinessModelCanvasResponse,
    ValidationRequest, ValidationResponse, CompareRequest, CompareResponse
)
from app.db.repositories.repos import OpportunityRepository
from app.db.sqlite import get_db
from app.models.models import Opportunity, OpportunityEvidence, BusinessModel, ValidationResult

router = APIRouter()

@router.get("/opportunities", response_model=List[OpportunityResponse], tags=["Opportunities"])
def get_opportunities(company_id: Optional[str] = None, db: Session = Depends(get_db)):
    """
    List all generated business opportunities. Can be filtered by company_id.
    """
    if company_id:
        opps = OpportunityRepository.get_by_company(db, company_id)
    else:
        opps = OpportunityRepository.get_all(db)
    return opps

@router.get("/opportunities/{opportunity_id}", response_model=OpportunityDetailResponse, tags=["Opportunities"])
def get_opportunity_detail(opportunity_id: str, db: Session = Depends(get_db)):
    """
    Retrieves full details for a specific opportunity including nested evidence and canvas model.
    """
    opp = OpportunityRepository.get_by_id(db, opportunity_id)
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found.")
    
    # Structure return data with relationships
    evidence_list = []
    for ev in opp.evidence:
        evidence_list.append(
            OpportunityEvidenceResponse(
                id=ev.id,
                opportunity_id=ev.opportunity_id,
                chunk_id=ev.chunk_id,
                asset_id=ev.asset_id,
                file_name=ev.asset.file_name,
                asset_type=ev.asset.asset_type,
                relevance_score=ev.relevance_score,
                supporting_text=ev.supporting_text
            )
        )
        
    validation_history = []
    for val in opp.validation_results:
        validation_history.append(ValidationResponse.model_validate(val))

    canvas = None
    if opp.business_model_canvas:
        canvas = BusinessModelCanvasResponse.model_validate(opp.business_model_canvas)

    res = OpportunityDetailResponse(
        id=opp.id,
        company_id=opp.company_id,
        title=opp.title,
        short_description=opp.short_description,
        overall_score=opp.overall_score,
        market_potential=opp.market_potential,
        feasibility=opp.feasibility,
        strategic_fit=opp.strategic_fit,
        asset_reusability=opp.asset_reusability,
        confidence=opp.confidence,
        industry=opp.industry,
        status=opp.status,
        created_at=opp.created_at,
        problem=opp.problem,
        solution=opp.solution,
        target_customers=opp.target_customers,
        business_model=opp.business_model,
        revenue_model=opp.revenue_model,
        required_resources=opp.required_resources,
        existing_assets_used=opp.existing_assets_used,
        key_activities=opp.key_activities,
        key_resources=opp.key_resources,
        cost_drivers=opp.cost_drivers,
        go_to_market=opp.go_to_market,
        risks=opp.risks,
        assumptions=opp.assumptions,
        reasoning=opp.reasoning,
        evidence=evidence_list,
        business_model_canvas=canvas,
        validation_results=validation_history
    )
    return res

@router.get("/opportunities/{opportunity_id}/evidence", response_model=List[OpportunityEvidenceResponse], tags=["Opportunities"])
def get_opportunity_evidence(opportunity_id: str, db: Session = Depends(get_db)):
    """
    Get all supporting chunks linked to this opportunity.
    """
    opp = OpportunityRepository.get_by_id(db, opportunity_id)
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found.")
        
    evidence_list = []
    for ev in opp.evidence:
        evidence_list.append(
            OpportunityEvidenceResponse(
                id=ev.id,
                opportunity_id=ev.opportunity_id,
                chunk_id=ev.chunk_id,
                asset_id=ev.asset_id,
                file_name=ev.asset.file_name,
                asset_type=ev.asset.asset_type,
                relevance_score=ev.relevance_score,
                supporting_text=ev.supporting_text
            )
        )
    return evidence_list

@router.get("/opportunities/{opportunity_id}/business-model", response_model=BusinessModelCanvasResponse, tags=["Opportunities"])
def get_opportunity_business_model(opportunity_id: str, db: Session = Depends(get_db)):
    """
    Get the Business Model Canvas structure of the opportunity.
    """
    opp = OpportunityRepository.get_by_id(db, opportunity_id)
    if not opp or not opp.business_model_canvas:
        raise HTTPException(status_code=404, detail="Business Model Canvas not found.")
    return opp.business_model_canvas

@router.post("/opportunities/{opportunity_id}/validate", response_model=ValidationResponse, tags=["Opportunities"])
def validate_opportunity(
    opportunity_id: str,
    req: ValidationRequest,
    db: Session = Depends(get_db)
):
    """
    Adjust score metrics manually, commit comments, and save changes to validate or reject a venture recommendation.
    """
    opp = OpportunityRepository.get_by_id(db, opportunity_id)
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found.")

    # Calculate overall score according to formula weights:
    # Market Potential: 25%
    # Feasibility: 25%
    # Strategic Fit: 20%
    # Asset Reusability: 15%
    # Confidence: 15%
    overall = (
        (req.market_potential * 0.25) + 
        (req.feasibility * 0.25) + 
        (req.strategic_fit * 0.20) + 
        (req.asset_reusability * 0.15) + 
        (req.confidence * 0.15)
    )
    
    # Save validation transaction
    val = OpportunityRepository.create_validation_result(
        db=db,
        opportunity_id=opportunity_id,
        market_potential=req.market_potential,
        feasibility=req.feasibility,
        strategic_fit=req.strategic_fit,
        asset_reusability=req.asset_reusability,
        confidence=req.confidence,
        overall_score=round(overall, 1),
        adjusted_by="Human Decider",
        comments=req.comments,
        status=req.status
    )
    return val

@router.post("/opportunities/compare", response_model=List[CompareResponse], tags=["Opportunities"])
def compare_opportunities(req: CompareRequest, db: Session = Depends(get_db)):
    """
    Returns side-by-side matrices of chosen opportunities for evaluation comparison.
    """
    output = []
    for opp_id in req.opportunity_ids:
        opp = OpportunityRepository.get_by_id(db, opp_id)
        if opp:
            output.append(
                CompareResponse(
                    id=opp.id,
                    title=opp.title,
                    overall_score=opp.overall_score,
                    market_potential=opp.market_potential,
                    feasibility=opp.feasibility,
                    strategic_fit=opp.strategic_fit,
                    asset_reusability=opp.asset_reusability,
                    confidence=opp.confidence,
                    short_description=opp.short_description,
                    industry=opp.industry,
                    business_model=opp.business_model,
                    revenue_model=opp.revenue_model,
                    required_resources=opp.required_resources,
                    risks=opp.risks
                )
            )
    return output
