import math
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from app.config import settings
from app.utils.logger import logger
from app.services.embeddings import EmbeddingService


def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    dot = sum(a * b for a, b in zip(v1, v2))
    norm1 = math.sqrt(sum(a * a for a in v1))
    norm2 = math.sqrt(sum(b * b for b in v2))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)


class QdrantService:
    def __init__(self):
        self.collection_name = settings.QDRANT_COLLECTION
        self.is_connected = False
        self.client = None
        self._memory_store: List[Dict[str, Any]] = []

        try:
            self.client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT, timeout=3.0)
            # Check server connection
            self.client.get_collections()
            self.is_connected = True
            logger.info(f"[QDRANT] Connected to Qdrant at {settings.QDRANT_HOST}:{settings.QDRANT_PORT}")
            self._ensure_collection()
        except Exception as e:
            logger.warning(f"[QDRANT] Could not connect to Qdrant daemon ({e}). Using robust local in-memory vector store.")
            self.is_connected = False

    def _ensure_collection(self):
        if not self.is_connected or not self.client:
            return
        try:
            collections = self.client.get_collections().collections
            exists = any(c.name == self.collection_name for c in collections)
            if not exists:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=qmodels.VectorParams(
                        size=384,  # default size for all-MiniLM-L6-v2
                        distance=qmodels.Distance.COSINE
                    )
                )
                logger.info(f"[QDRANT] Created collection '{self.collection_name}' with 384 dimensions.")
        except Exception as e:
            logger.warning(f"[QDRANT] Error ensuring collection: {e}")
            self.is_connected = False

    def insert_chunks(self, chunks: List[Dict[str, Any]]) -> bool:
        if not chunks:
            return True

        contents = [c["content"] for c in chunks]
        embeddings = EmbeddingService.generate_embeddings(contents)

        if self.is_connected and self.client:
            try:
                points = []
                for idx, (chunk, vector) in enumerate(zip(chunks, embeddings)):
                    point_id = str(chunk.get("chunk_id"))
                    payload = {
                        "document_id": chunk.get("document_id"),
                        "source_file": chunk.get("source_file"),
                        "content": chunk.get("content"),
                        "asset_type": chunk.get("asset_type"),
                        "company": chunk.get("company"),
                        "page_number": chunk.get("page_number"),
                        "section_title": chunk.get("section_title"),
                        "timestamp": chunk.get("timestamp"),
                        "metadata": chunk.get("metadata", {})
                    }
                    points.append(qmodels.PointStruct(
                        id=point_id,
                        vector=vector,
                        payload=payload
                    ))
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=points
                )
                logger.info(f"[QDRANT] Successfully indexed {len(points)} points into Qdrant.")
                return True
            except Exception as e:
                logger.warning(f"[QDRANT] Failed to upsert to Qdrant daemon ({e}). Falling back to memory store.")
                self.is_connected = False

        # In-memory store fallback
        for chunk, vector in zip(chunks, embeddings):
            self._memory_store.append({
                "id": chunk.get("chunk_id"),
                "vector": vector,
                "payload": {
                    "document_id": chunk.get("document_id"),
                    "source_file": chunk.get("source_file"),
                    "content": chunk.get("content"),
                    "asset_type": chunk.get("asset_type"),
                    "company": chunk.get("company"),
                    "page_number": chunk.get("page_number"),
                    "section_title": chunk.get("section_title"),
                    "timestamp": chunk.get("timestamp"),
                    "metadata": chunk.get("metadata", {})
                }
            })
        logger.info(f"[QDRANT-MEMORY] Stored {len(chunks)} points in fallback memory vector store (total: {len(self._memory_store)}).")
        return True

    def search(
        self,
        query: str,
        top_k: int = 5,
        asset_type_filter: Optional[str] = None,
        company_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        query_vector = EmbeddingService.generate_embedding(query)

        if self.is_connected and self.client:
            try:
                must_filters = []
                if asset_type_filter:
                    must_filters.append(qmodels.FieldCondition(
                        key="asset_type",
                        match=qmodels.MatchValue(value=asset_type_filter)
                    ))
                if company_filter:
                    must_filters.append(qmodels.FieldCondition(
                        key="company",
                        match=qmodels.MatchValue(value=company_filter)
                    ))

                filter_obj = qmodels.Filter(must=must_filters) if must_filters else None

                results = self.client.search(
                    collection_name=self.collection_name,
                    query_vector=query_vector,
                    query_filter=filter_obj,
                    limit=top_k
                )

                items = []
                for res in results:
                    items.append({
                        "score": float(res.score),
                        "content": res.payload.get("content"),
                        "source_file": res.payload.get("source_file"),
                        "asset_type": res.payload.get("asset_type"),
                        "company": res.payload.get("company"),
                        "page_number": res.payload.get("page_number"),
                        "section_title": res.payload.get("section_title"),
                        "document_id": res.payload.get("document_id")
                    })
                return items
            except Exception as e:
                logger.warning(f"[QDRANT] Search failed on daemon ({e}). Falling back to memory store.")

        # In-memory cosine search fallback
        scored_items = []
        for item in self._memory_store:
            payload = item["payload"]
            if asset_type_filter and payload.get("asset_type") != asset_type_filter:
                continue
            if company_filter and payload.get("company") != company_filter:
                continue

            sim = cosine_similarity(query_vector, item["vector"])
            scored_items.append({
                "score": float(sim),
                "content": payload.get("content"),
                "source_file": payload.get("source_file"),
                "asset_type": payload.get("asset_type"),
                "company": payload.get("company"),
                "page_number": payload.get("page_number"),
                "section_title": payload.get("section_title"),
                "document_id": payload.get("document_id")
            })

        scored_items.sort(key=lambda x: x["score"], reverse=True)
        return scored_items[:top_k]


qdrant_service = QdrantService()
