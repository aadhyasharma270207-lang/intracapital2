import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db import models
from app.schemas.opportunities import (
    DiscoverOpportunitiesRequest,
    DiscoverOpportunitiesResponse,
    OpportunityResponse,
    ExplainOpportunityResponse
)
from app.services.rag_service import rag_service
from app.services.neo4j_service import neo4j_service
from app.services.granite_service import granite_service
from app.agents.orchestrator import PipelineOrchestrator
from app.utils.logger import logger

router = APIRouter()


@router.post("/opportunities/discover", response_model=DiscoverOpportunitiesResponse)
def discover_opportunities(
    req: DiscoverOpportunitiesRequest = DiscoverOpportunitiesRequest(),
    db: Session = Depends(get_db)
):
    company_name = req.company_name or "Intracapital Corp"
    company = db.query(models.Company).filter(models.Company.name == company_name).first()

    if not company:
        company = models.Company(name=company_name, industry="General")
        db.add(company)
        db.commit()
        db.refresh(company)

    # 1. Load company assets
    db_assets = db.query(models.Asset).filter(models.Asset.company_id == company.id).all()
    assets_data = [
        {
            "id": a.id,
            "name": a.name,
            "asset_type": a.asset_type,
            "description": a.description,
            "source_file": a.source_file
        } for a in db_assets
    ]

    # 2. Query Knowledge Graph
    graph_context = neo4j_service.get_opportunity_context()

    # 3. Retrieve RAG Evidence
    rag_context = rag_service.retrieve_context(
        query=f"Business opportunity and underutilized technology assets for {company_name}",
        top_k=10
    )
    rag_evidence = rag_context.get("vector_evidence", [])

    # 4. Create AnalysisRun in DB
    analysis_id = str(uuid.uuid4())
    analysis_run = models.AnalysisRun(
        id=analysis_id,
        company_id=company.id,
        status="running"
    )
    db.add(analysis_run)
    db.commit()

    # 5. Run Multi-Agent Orchestrator Pipeline
    workflow_result = PipelineOrchestrator.run_discovery_pipeline(
        company_id=company.id,
        company_name=company_name,
        enterprise_assets=assets_data,
        rag_evidence=rag_evidence,
        graph_context=graph_context,
        analysis_id=analysis_id
    )

    ranked_opps = workflow_result.get("ranked_opportunities", [])

    # 6. Save opportunities and deterministic scores to SQLite
    opp_responses = []
    for idx, opp in enumerate(ranked_opps):
        opp_code = opp.get("opportunity_id", f"OPP-{(idx+1):03d}")
        score_breakdown = opp.get("scores_breakdown", {})
        overall_score = opp.get("score", 85.0)

        db_opp = models.Opportunity(
            id=str(uuid.uuid4()),
            analysis_run_id=analysis_id,
            opportunity_code=opp_code,
            name=opp.get("name", "New Opportunity"),
            score=overall_score,
            problem=opp.get("problem", ""),
            solution=opp.get("solution", ""),
            business_model=opp.get("business_model", ""),
            revenue_model=opp.get("revenue_model", ""),
            reasoning=opp.get("reasoning", ""),
            target_customers=opp.get("target_customers", []),
            target_industries=opp.get("target_industries", []),
            reused_assets=opp.get("reused_assets", []),
            implementation_plan=opp.get("implementation_plan", []),
            risks=opp.get("risks", [])
        )
        db.add(db_opp)
        db.commit()
        db.refresh(db_opp)

        db_score = models.OpportunityScore(
            opportunity_id=db_opp.id,
            market_potential=score_breakdown.get("market_potential", 85.0),
            feasibility=score_breakdown.get("feasibility", 88.0),
            strategic_fit=score_breakdown.get("strategic_fit", 82.0),
            asset_reusability=score_breakdown.get("asset_reusability", 90.0),
            confidence=score_breakdown.get("confidence", 85.0),
            overall_score=overall_score
        )
        db.add(db_score)

        # Save Evidence
        for ev in opp.get("evidence", []):
            db_ev = models.Evidence(
                opportunity_id=db_opp.id,
                source_file=ev if isinstance(ev, str) else ev.get("source_file", "Enterprise File"),
                content_snippet=f"Documented evidence for {opp.get('name')}",
                asset_name=ev if isinstance(ev, str) else ev.get("asset_name")
            )
            db.add(db_ev)

        db.commit()

        opp_responses.append(OpportunityResponse(
            opportunity_id=opp_code,
            name=opp.get("name"),
            score=overall_score,
            market_potential=score_breakdown.get("market_potential", 85.0),
            feasibility=score_breakdown.get("feasibility", 88.0),
            strategic_fit=score_breakdown.get("strategic_fit", 82.0),
            asset_reusability=score_breakdown.get("asset_reusability", 90.0),
            confidence=score_breakdown.get("confidence", 85.0),
            problem=opp.get("problem", ""),
            solution=opp.get("solution", ""),
            target_customers=opp.get("target_customers", []),
            target_industries=opp.get("target_industries", []),
            business_model=opp.get("business_model", ""),
            revenue_model=opp.get("revenue_model", ""),
            reused_assets=opp.get("reused_assets", []),
            implementation_plan=opp.get("implementation_plan", []),
            risks=opp.get("risks", []),
            evidence=opp.get("evidence", []),
            reasoning=opp.get("reasoning", "")
        ))

    analysis_run.status = "completed"
    analysis_run.opportunities_discovered = len(opp_responses)
    db.commit()

    return DiscoverOpportunitiesResponse(
        analysis_id=analysis_id,
        company_name=company_name,
        opportunities_discovered=len(opp_responses),
        opportunities=opp_responses
    )


@router.get("/opportunities", response_model=List[OpportunityResponse])
def list_opportunities(db: Session = Depends(get_db)):
    opps = db.query(models.Opportunity).all()
    output = []
    for o in opps:
        score_rec = o.score_details
        mp = score_rec.market_potential if score_rec else 85.0
        fe = score_rec.feasibility if score_rec else 88.0
        sf = score_rec.strategic_fit if score_rec else 82.0
        ar = score_rec.asset_reusability if score_rec else 90.0
        cf = score_rec.confidence if score_rec else 85.0

        output.append(OpportunityResponse(
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
    return output


@router.get("/opportunities/{opportunity_id}", response_model=OpportunityResponse)
def get_opportunity(opportunity_id: str, db: Session = Depends(get_db)):
    opp = db.query(models.Opportunity).filter(
        (models.Opportunity.opportunity_code == opportunity_id) | (models.Opportunity.id == opportunity_id)
    ).first()

    if not opp:
        raise HTTPException(status_code=404, detail=f"Opportunity '{opportunity_id}' not found.")

    score_rec = opp.score_details
    mp = score_rec.market_potential if score_rec else 85.0
    fe = score_rec.feasibility if score_rec else 88.0
    sf = score_rec.strategic_fit if score_rec else 82.0
    ar = score_rec.asset_reusability if score_rec else 90.0
    cf = score_rec.confidence if score_rec else 85.0

    return OpportunityResponse(
        opportunity_id=opp.opportunity_code,
        name=opp.name,
        score=opp.score,
        market_potential=mp,
        feasibility=fe,
        strategic_fit=sf,
        asset_reusability=ar,
        confidence=cf,
        problem=opp.problem,
        solution=opp.solution,
        target_customers=opp.target_customers or [],
        target_industries=opp.target_industries or [],
        business_model=opp.business_model,
        revenue_model=opp.revenue_model,
        reused_assets=opp.reused_assets or [],
        implementation_plan=opp.implementation_plan or [],
        risks=opp.risks or [],
        evidence=[e.source_file for e in opp.evidence_list],
        reasoning=opp.reasoning
    )


@router.post("/opportunities/{opportunity_id}/explain", response_model=ExplainOpportunityResponse)
def explain_opportunity(opportunity_id: str, db: Session = Depends(get_db)):
    opp = db.query(models.Opportunity).filter(
        (models.Opportunity.opportunity_code == opportunity_id) | (models.Opportunity.id == opportunity_id)
    ).first()

    if not opp:
        raise HTTPException(status_code=404, detail=f"Opportunity '{opportunity_id}' not found.")

    score_rec = opp.score_details
    score_map = {
        "market_potential": score_rec.market_potential if score_rec else 85.0,
        "feasibility": score_rec.feasibility if score_rec else 88.0,
        "strategic_fit": score_rec.strategic_fit if score_rec else 82.0,
        "asset_reusability": score_rec.asset_reusability if score_rec else 90.0,
        "confidence": score_rec.confidence if score_rec else 85.0,
        "overall_score": opp.score
    }

    graph_context = neo4j_service.get_opportunity_context()

    explanation = opp.reasoning
    if not explanation or "Granite thinks" in explanation:
        explanation = (
            f"Opportunity '{opp.name}' was generated because the company already owns "
            f"{', '.join(opp.reused_assets or ['internal sensor datasets', 'patents'])}, "
            f"and these assets are connected through graph capabilities. Customer feedback indicates problem '{opp.problem}'."
        )

    return ExplainOpportunityResponse(
        opportunity_id=opp.opportunity_code,
        name=opp.name,
        score=opp.score,
        explanation=explanation,
        cited_assets=opp.reused_assets or [],
        graph_relationships=graph_context.get("relationships", []),
        score_breakdown=score_map
    )
