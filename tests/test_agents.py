from app.agents.data_agent import DataAnalysisAgent
from app.agents.market_agent import MarketResearchAgent
from app.agents.innovation_agent import InnovationAgent
from app.agents.state import DiscoveryState


def test_agent_pipeline():
    state: DiscoveryState = {
        "company_id": "test-c1",
        "company_name": "Test Co",
        "enterprise_assets": [{"name": "Thermal Sensor Log", "asset_type": "SENSOR_DATA"}],
        "rag_evidence": [],
        "graph_context": {"nodes": [], "relationships": []},
        "underutilized_assets": [],
        "capabilities": [],
        "market_research": {},
        "candidate_opportunities": [],
        "evaluated_opportunities": [],
        "ranked_opportunities": [],
        "analysis_id": "test-a1"
    }

    state = DataAnalysisAgent.run(state)
    assert len(state["capabilities"]) >= 1

    state = MarketResearchAgent.run(state)
    assert "target_industries" in state["market_research"]

    state = InnovationAgent.run(state)
    assert len(state["candidate_opportunities"]) >= 1
