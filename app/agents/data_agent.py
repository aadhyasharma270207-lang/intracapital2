from typing import Dict, Any, List
from app.agents.state import DiscoveryState
from app.services.granite_service import granite_service
from app.utils.logger import logger


class DataAnalysisAgent:
    @staticmethod
    def run(state: DiscoveryState) -> DiscoveryState:
        logger.info("[AGENT] Running Data Analysis Agent...")
        assets = state.get("enterprise_assets", [])
        graph = state.get("graph_context", {})

        prompt = (
            "Analyze these enterprise assets and knowledge graph context:\n"
            f"Assets: {assets}\n"
            f"Graph: {graph}\n\n"
            "Identify:\n"
            "1. underutilized_assets (list of objects with name and reason)\n"
            "2. capabilities (list of strings)\n"
            "3. potential_asset_combinations (list of objects with combined_assets and concept)\n\n"
            "Return JSON matching keys: underutilized_assets, capabilities, potential_asset_combinations."
        )

        analysis = granite_service.generate_json(prompt)
        state["underutilized_assets"] = analysis.get("underutilized_assets", [
            {"name": a.get("name", "Asset"), "reason": "High secondary deployment potential"} for a in assets
        ])
        state["capabilities"] = analysis.get("capabilities", [
            "Thermal Monitoring & Sensing",
            "Predictive Quality Control",
            "IoT Data Ingestion"
        ])
        return state
