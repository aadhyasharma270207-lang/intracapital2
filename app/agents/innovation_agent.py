from typing import Dict, Any, List
from app.agents.state import DiscoveryState
from app.services.granite_service import granite_service
from app.utils.logger import logger


class InnovationAgent:
    @staticmethod
    def run(state: DiscoveryState) -> DiscoveryState:
        logger.info("[AGENT] Running Innovation Agent...")
        assets = state.get("enterprise_assets", [])
        evidence = state.get("rag_evidence", [])
        graph = state.get("graph_context", {})
        market = state.get("market_research", {})

        opportunities = granite_service.generate_opportunity(
            enterprise_assets=assets,
            rag_evidence=evidence,
            graph_relationships=graph.get("relationships", []),
            market_context=market
        )

        # Fallback to guarantee at least 3 distinct opportunities if model output was sparse
        if not opportunities or len(opportunities) < 3:
            opportunities = InnovationAgent._get_default_opportunities(assets)

        state["candidate_opportunities"] = opportunities
        return state

    @staticmethod
    def _get_default_opportunities(assets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        asset_names = [a.get("name", "Enterprise Asset") for a in assets]
        return [
            {
                "name": "Cold Chain Intelligence Platform",
                "problem": "Frequent perishable freight spoilage due to undetected temperature threshold violations during transit.",
                "solution": "An automated IoT cold chain monitoring platform combining internal thermal sensor patents, vehicle telemetry, and predictive risk analytics.",
                "reused_assets": asset_names[:3] if len(asset_names) >= 3 else asset_names,
                "target_customers": ["Pharmaceutical Distributors", "Perishable Freight Carriers"],
                "target_industries": ["Cold Chain Logistics", "Healthcare & Pharma"],
                "value_proposition": "Real-time spoilage prevention and automated regulatory compliance using existing thermal patents.",
                "business_model": "B2B Enterprise SaaS per connected vehicle/unit.",
                "revenue_model": "Recurring annual subscriptions + hardware onboarding packages.",
                "implementation_plan": ["Integrate sensor data pipeline", "Deploy Granite predictive model", "Launch client dashboard"],
                "competitive_advantage": "Proprietary patented thermal monitoring algorithms integrated into live IoT sensor streams.",
                "risks": ["Telemetry loss in low-connectivity areas", "Sensor calibration drift"],
                "evidence": ["Warehouse Temperature Sensor Dataset", "Thermal Monitoring Patent US-984512-B2"]
            },
            {
                "name": "Predictive Equipment Maintenance Platform",
                "problem": "Costly unplanned manufacturing downtime and component overheating in factory assembly lines.",
                "solution": "An enterprise predictive maintenance engine utilizing internal thermal imaging logs, vibration metrics, and anomaly detection models.",
                "reused_assets": asset_names[1:4] if len(asset_names) >= 4 else asset_names,
                "target_customers": ["Factory Operations Managers", "Heavy Machinery Operators"],
                "target_industries": ["Smart Manufacturing", "Industrial Automation"],
                "value_proposition": "Drastic reduction in equipment downtime through 48-hour advance failure forecasting.",
                "business_model": "Per-machine monthly subscription tier.",
                "revenue_model": "Base SaaS license + tier per monitored production line.",
                "implementation_plan": ["Hook IoT telemetry logs to feature store", "Train local baseline anomaly detectors", "Roll out alerting dashboard"],
                "competitive_advantage": "Built directly on company's historic manufacturing logs and sensor calibrations.",
                "risks": ["Noisy factory telemetry environments", "Resistance to process change"],
                "evidence": ["Manufacturing IoT Log Dataset", "HVAC Specs Document"]
            },
            {
                "name": "Urban Footfall & Commercial Intelligence Platform",
                "problem": "Commercial real estate developers lack precise ambient environmental and traffic intelligence to price retail spaces.",
                "solution": "A location analytics suite repurposing retail customer feedback, ambient IoT sensors, and footfall heatmaps into commercial intelligence.",
                "reused_assets": [asset_names[0]] if asset_names else ["Customer Feedback CSV"],
                "target_customers": ["Real Estate Developers", "Urban Retail Chains"],
                "target_industries": ["Commercial Real Estate", "Retail Analytics"],
                "value_proposition": "Data-backed site selection and dynamic rent pricing using proprietary internal datasets.",
                "business_model": "Data API licensing and quarterly analytics report subscriptions.",
                "revenue_model": "API volume pricing + custom enterprise report fees.",
                "implementation_plan": ["Aggregate customer location feedback", "Build footfall heatmap models", "Release developer API"],
                "competitive_advantage": "Proprietary historical customer sentiment and location dataset.",
                "risks": ["Data anonymization compliance", "Competitor real estate APIs"],
                "evidence": ["Customer Feedback CSV", "Logistics Cold Chain Report"]
            }
        ]
