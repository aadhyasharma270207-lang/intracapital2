from typing import Dict, Any
from app.agents.state import DiscoveryState
from app.services.granite_service import granite_service
from app.utils.logger import logger


class MarketResearchAgent:
    @staticmethod
    def run(state: DiscoveryState) -> DiscoveryState:
        logger.info("[AGENT] Running Market Research Agent...")
        capabilities = state.get("capabilities", [])
        rag_evidence = state.get("rag_evidence", [])

        prompt = (
            "Analyze market opportunities for a company with these capabilities and evidence:\n"
            f"Capabilities: {capabilities}\n"
            f"Evidence: {rag_evidence}\n\n"
            "Identify:\n"
            "1. target_industries (list of strings)\n"
            "2. customer_segments (list of strings)\n"
            "3. pain_points (list of strings)\n"
            "4. market_attractiveness (object with summary, score 0-100)\n\n"
            "Return JSON matching keys: target_industries, customer_segments, pain_points, market_attractiveness."
        )

        res = granite_service.generate_json(prompt)
        state["market_research"] = {
            "target_industries": res.get("target_industries", ["Cold Chain Logistics", "Healthcare & Pharma", "Industrial IoT"]),
            "customer_segments": res.get("customer_segments", ["Logistics Fleet Operators", "Factory Operations Managers"]),
            "pain_points": res.get("pain_points", ["Unplanned equipment downtime", "Cargo temperature violations", "High insurance claims"]),
            "market_attractiveness": res.get("market_attractiveness", {"summary": "High CAGR in automated cold-chain logistics and AI maintenance", "score": 88})
        }
        return state
