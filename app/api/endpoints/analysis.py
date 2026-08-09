from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db import models
from app.schemas.opportunities import OpportunityResponse

router = APIRouter()


@router.get("/analysis/{analysis_id}")
def get_analysis_run(analysis_id: str, db: Session = Depends(get_db)):
    run = db.query(models.AnalysisRun).filter(models.AnalysisRun.id == analysis_id).first()
    if not run:
        raise HTTPException(status_code=404, detail=f"Analysis run '{analysis_id}' not found.")

    opps = []
    for o in run.opportunities:
        score_rec = o.score_details
        mp = score_rec.market_potential if score_rec else 85.0
        fe = score_rec.feasibility if score_rec else 88.0
        sf = score_rec.strategic_fit if score_rec else 82.0
        ar = score_rec.asset_reusability if score_rec else 90.0
        cf = score_rec.confidence if score_rec else 85.0

        opps.append(OpportunityResponse(
            opportunity_id=o.opportunity_code,
            name=o.name,
            score=o.score,
            market_potential=mp,
            feasibility=fe,
            strategic_fit=sf,
            asset_reusability=ar,
            confidence=cf,
            problem=o.problem,
            solution=o.solution,
            target_customers=o.target_customers or [],
            target_industries=o.target_industries or [],
            business_model=o.business_model,
            revenue_model=o.revenue_model,
            reused_assets=o.reused_assets or [],
            implementation_plan=o.implementation_plan or [],
            risks=o.risks or [],
            evidence=[e.source_file for e in o.evidence_list],
            reasoning=o.reasoning
        ))

    return {
        "analysis_id": run.id,
        "company_id": run.company_id,
        "status": run.status,
        "opportunities_discovered": run.opportunities_discovered,
        "created_at": run.created_at.isoformat() if run.created_at else "",
        "opportunities": opps
    }
