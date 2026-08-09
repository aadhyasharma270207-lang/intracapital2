from typing import List, Dict, Any, Optional
from app.services.qdrant_service import qdrant_service
from app.services.neo4j_service import neo4j_service
from app.utils.logger import logger


class RAGService:
    @staticmethod
    def retrieve_context(query: str, top_k: int = 5) -> Dict[str, Any]:
        logger.info(f"[RAG] Retrieving context for query: '{query}'")
        vector_results = qdrant_service.search(query=query, top_k=top_k)
        graph_context = neo4j_service.get_opportunity_context()

        return {
            "query": query,
            "vector_evidence": vector_results,
            "graph_evidence": graph_context
        }

    @staticmethod
    def retrieve_asset_context(asset_id: str) -> Dict[str, Any]:
        logger.info(f"[RAG] Retrieving context for asset_id: {asset_id}")
        graph_neighbors = neo4j_service.find_related_assets(asset_id)
        vector_chunks = qdrant_service.search(query=f"Asset ID {asset_id}", top_k=5)

        return {
            "asset_id": asset_id,
            "graph_relationships": graph_neighbors,
            "vector_chunks": vector_chunks
        }

    @staticmethod
    def retrieve_opportunity_evidence(asset_names: List[str]) -> List[Dict[str, Any]]:
        evidence = []
        for name in asset_names:
            chunks = qdrant_service.search(query=name, top_k=3)
            for chunk in chunks:
                evidence.append({
                    "asset_name": name,
                    "source_file": chunk.get("source_file"),
                    "content_snippet": chunk.get("content"),
                    "score": chunk.get("score", 1.0)
                })
        return evidence

    @staticmethod
    def retrieve_similar_assets(query_asset_desc: str, top_k: int = 3) -> List[Dict[str, Any]]:
        return qdrant_service.search(query=query_asset_desc, top_k=top_k)


rag_service = RAGService()
