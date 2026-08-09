from typing import Dict, Any, List
from app.agents.state import DiscoveryState
from app.services.granite_service import granite_service
from app.utils.logger import logger


class EvaluationAgent:
    @staticmethod
    def calculate_score(
        market_potential: float,
        feasibility: float,
        strategic_fit: float,
        asset_reusability: float,
        confidence: float
    ) -> float:
        # Enforce 0-100 bounds
        mp = max(0.0, min(100.0, float(market_potential)))
        fe = max(0.0, min(100.0, float(feasibility)))
        sf = max(0.0, min(100.0, float(strategic_fit)))
        ar = max(0.0, min(100.0, float(asset_reusability)))
        cf = max(0.0, min(100.0, float(confidence)))

        score = (0.30 * mp) + (0.25 * fe) + (0.20 * sf) + (0.15 * ar) + (0.10 * cf)
        return round(score, 1)

    @staticmethod
    def run(state: DiscoveryState) -> DiscoveryState:
        logger.info("[AGENT] Running Evaluation Agent with Deterministic Scoring...")
        candidates = state.get("candidate_opportunities", [])
        evaluated = []

        for idx, opp in enumerate(candidates):
            # Ask Granite for component dimension evaluations
            dim_scores = granite_service.evaluate_opportunity(opp)

            mp = dim_scores.get("market_potential", 85.0)
            fe = dim_scores.get("feasibility", 88.0)
            sf = dim_scores.get("strategic_fit", 82.0)
            ar = dim_scores.get("asset_reusability", 90.0)
            cf = dim_scores.get("confidence", 85.0)

            # DETERMINISTIC FORMULA CALCULATION
            overall_score = EvaluationAgent.calculate_score(
                market_potential=mp,
                feasibility=fe,
                strategic_fit=sf,
                asset_reusability=ar,
                confidence=cf
            )

            opp_copy = dict(opp)
            opp_copy["opportunity_id"] = f"OPP-{(idx + 1):03d}"
            opp_copy["score"] = overall_score
            opp_copy["scores_breakdown"] = {
                "market_potential": mp,
                "feasibility": fe,
                "strategic_fit": sf,
                "asset_reusability": ar,
                "confidence": cf,
                "overall_score": overall_score
            }

            # Generate explainability reasoning
            reasoning = granite_service.explain_opportunity(
                opportunity=opp_copy,
                evidence=opp_copy.get("evidence", [])
            )
            opp_copy["reasoning"] = reasoning

            evaluated.append(opp_copy)

        # Deduplicate & Rank by overall_score descending
        ranked = sorted(evaluated, key=lambda x: x["score"], reverse=True)
        state["evaluated_opportunities"] = evaluated
        state["ranked_opportunities"] = ranked

        return state
