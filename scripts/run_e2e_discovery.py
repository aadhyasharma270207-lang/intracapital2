import json
from app.db.database import SessionLocal, init_db
from app.db import models
from app.api.endpoints.opportunities import discover_opportunities
from app.schemas.opportunities import DiscoverOpportunitiesRequest
from app.utils.logger import logger


def run():
    init_db()
    db = SessionLocal()
    logger.info("================================================================================")
    logger.info("  INTRACAPITAL — DISCOVERING BUSINESSES HIDDEN INSIDE BUSINESSES (LOCAL E2E)")
    logger.info("================================================================================")

    req = DiscoverOpportunitiesRequest(company_name="Intracapital Corp")
    resp = discover_opportunities(req=req, db=db)

    print("\n--------------------------------------------------------------------------------")
    print(f"ANALYSIS RUN ID: {resp.analysis_id}")
    print(f"COMPANY NAME:    {resp.company_name}")
    print(f"OPPORTUNITIES DISCOVERED: {resp.opportunities_discovered}")
    print("--------------------------------------------------------------------------------\n")

    for idx, opp in enumerate(resp.opportunities, 1):
        print(f"[{idx}] {opp.name} ({opp.opportunity_id})")
        print(f"    SCORE:             {opp.score}/100")
        print(f"    SCORE BREAKDOWN:   Market Potential={opp.market_potential}, Feasibility={opp.feasibility}, Strategic Fit={opp.strategic_fit}, Reusability={opp.asset_reusability}, Confidence={opp.confidence}")
        print(f"    PROBLEM:           {opp.problem}")
        print(f"    SOLUTION:          {opp.solution}")
        print(f"    REUSED ASSETS:     {', '.join(opp.reused_assets)}")
        print(f"    TARGET CUSTOMERS:  {', '.join(opp.target_customers)}")
        print(f"    VALUE PROP:        {opp.reasoning or opp.solution}")
        print(f"    EXPLANATION:       Opportunity was generated because company owns {', '.join(opp.reused_assets)} connected through thermal & IoT capabilities.")
        print("-" * 80)

    db.close()


if __name__ == "__main__":
    run()
