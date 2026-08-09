from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.schemas.schemas import AnalyticsResponse, CategoryCount, ScoreDistribution
from app.db.sqlite import get_db
from app.models.models import Asset, Opportunity, AssetChunk
from app.services.graph_service import GraphService

router = APIRouter()

@router.get("/analytics", response_model=AnalyticsResponse, tags=["Analytics"])
def get_analytics(db: Session = Depends(get_db)):
    """
    Computes system aggregate metrics, scoring distributions, and asset utilization percentages
    for analytics dashboards.
    """
    total_assets = db.query(Asset).count()
    processed_assets = db.query(Asset).filter(Asset.status == "processed").count()
    failed_assets = db.query(Asset).filter(Asset.status == "failed").count()
    total_opportunities = db.query(Opportunity).count()

    # Averages
    avg_score = db.query(func.avg(Opportunity.overall_score)).scalar() or 0.0
    avg_conf = db.query(func.avg(Opportunity.confidence)).scalar() or 0.0

    # Asset types distribution
    asset_types = db.query(
        Asset.asset_type, func.count(Asset.id)
    ).group_by(Asset.asset_type).all()
    
    asset_dist = [CategoryCount(name=row[0], count=row[1]) for row in asset_types]

    # Industry distribution
    industries = db.query(
        Opportunity.industry, func.count(Opportunity.id)
    ).group_by(Opportunity.industry).all()
    
    industry_dist = [CategoryCount(name=row[0], count=row[1]) for row in industries]

    # Score distribution ranges (0-50, 50-70, 70-80, 80-90, 90-100)
    score_ranges = {
        "Below 50": 0,
        "50-70": 0,
        "70-80": 0,
        "80-90": 0,
        "90-100": 0
    }
    
    opps_scores = db.query(Opportunity.overall_score).all()
    for row in opps_scores:
        score = row[0]
        if score < 50:
            score_ranges["Below 50"] += 1
        elif score < 70:
            score_ranges["50-70"] += 1
        elif score < 80:
            score_ranges["70-80"] += 1
        elif score < 90:
            score_ranges["80-90"] += 1
        else:
            score_ranges["90-100"] += 1
            
    score_dist = [ScoreDistribution(range=k, count=v) for k, v in score_ranges.items()]

    # Calculate asset utilization rate: percentage of processed assets linked to opportunities via evidence
    used_assets = db.query(func.count(func.distinct(Asset.id))).join(Asset.evidences).scalar() or 0
    util_rate = (used_assets / total_assets * 100) if total_assets > 0 else 0.0

    # Get connection stats from the Knowledge Graph
    graph_data = GraphService.get_entire_graph()
    total_connections = len(graph_data.get("edges", []))

    return AnalyticsResponse(
        total_assets=total_assets,
        processed_assets=processed_assets,
        failed_assets=failed_assets,
        total_opportunities=total_opportunities,
        average_overall_score=round(float(avg_score), 1),
        average_confidence=round(float(avg_conf), 1),
        asset_types_distribution=asset_dist,
        industry_distribution=industry_dist,
        opportunity_score_distribution=score_dist,
        asset_utilization_rate=round(float(util_rate), 1),
        total_connections=total_connections
    )
