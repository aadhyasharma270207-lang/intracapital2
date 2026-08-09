from langgraph.graph import StateGraph, END
from app.agents.state import DiscoveryState
from app.agents.data_agent import DataAnalysisAgent
from app.agents.market_agent import MarketResearchAgent
from app.agents.innovation_agent import InnovationAgent
from app.agents.evaluation_agent import EvaluationAgent
from app.utils.logger import logger


def build_discovery_graph():
    builder = StateGraph(DiscoveryState)

    builder.add_node("data_analysis", DataAnalysisAgent.run)
    builder.add_node("market_research", MarketResearchAgent.run)
    builder.add_node("innovation", InnovationAgent.run)
    builder.add_node("evaluation", EvaluationAgent.run)

    builder.set_entry_point("data_analysis")

    builder.add_edge("data_analysis", "market_research")
    builder.add_edge("market_research", "innovation")
    builder.add_edge("innovation", "evaluation")
    builder.add_edge("evaluation", END)

    return builder.compile()


discovery_workflow = build_discovery_graph()


class PipelineOrchestrator:
    @staticmethod
    def run_discovery_pipeline(
        company_id: str,
        company_name: str,
        enterprise_assets: list,
        rag_evidence: list,
        graph_context: dict,
        analysis_id: str = None
    ) -> dict:
        logger.info(f"[ORCHESTRATOR] Starting discovery workflow pipeline for {company_name} (ID: {company_id})...")

        initial_state: DiscoveryState = {
            "company_id": company_id,
            "company_name": company_name,
            "enterprise_assets": enterprise_assets,
            "rag_evidence": rag_evidence,
            "graph_context": graph_context,
            "underutilized_assets": [],
            "capabilities": [],
            "market_research": {},
            "candidate_opportunities": [],
            "evaluated_opportunities": [],
            "ranked_opportunities": [],
            "analysis_id": analysis_id
        }

        final_state = discovery_workflow.invoke(initial_state)
        logger.info(f"[ORCHESTRATOR] Pipeline complete. Discovered {len(final_state.get('ranked_opportunities', []))} ranked opportunities.")
        return final_state
