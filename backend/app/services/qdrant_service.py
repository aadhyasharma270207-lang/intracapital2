import logging
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from qdrant_client.http.exceptions import UnexpectedResponse
from app.core.config import settings

logger = logging.getLogger(__name__)

class QdrantService:
    _client: Optional[QdrantClient] = None
    _is_fallback: bool = False

    @classmethod
    def get_client(cls) -> QdrantClient:
        """
        Retrieves the QdrantClient instance. Connects to local/Docker container if available,
        falling back to a local in-memory instance if QDRANT_URL is offline.
        """
        if cls._client is not None:
            return cls._client

        # Try connecting to external Qdrant (Docker)
        if settings.QDRANT_URL:
            try:
                # Remove protocol scheme if needed, or parse accordingly
                client = QdrantClient(url=settings.QDRANT_URL, timeout=3.0)
                # Verify connection by calling a minor API
                client.get_collections()
                cls._client = client
                cls._is_fallback = False
                logger.info(f"Connected to external Qdrant at {settings.QDRANT_URL}")
                return cls._client
            except Exception as e:
                logger.warning(f"Could not connect to external Qdrant at {settings.QDRANT_URL}: {str(e)}")

        # Fallback to local in-memory database
        logger.info("Initializing in-memory local Qdrant client fallback.")
        cls._client = QdrantClient(location=":memory:")
        cls._is_fallback = True
        return cls._client

    @classmethod
    def check_status(cls) -> Dict[str, Any]:
        """
        Check connectivity to the vector database.
        """
        client = cls.get_client()
        if cls._is_fallback:
            return {
                "status": "DEGRADED",
                "message": "Docker Qdrant offline. Utilizing local in-memory vector storage fallback.",
                "details": {"type": "in-memory"}
            }
        else:
            try:
                collections = client.get_collections()
                return {
                    "status": "ONLINE",
                    "message": "Connected to Qdrant vector database.",
                    "details": {"collections_count": len(collections.collections)}
                }
            except Exception as e:
                return {
                    "status": "OFFLINE",
                    "message": f"Failed connection to Qdrant client: {str(e)}",
                    "details": {}
                }

    @classmethod
    def ensure_collection(cls, collection_name: str, vector_size: int = 384):
        """
        Ensure a collection exists with the specified vector configuration.
        """
        client = cls.get_client()
        try:
            client.get_collection(collection_name)
            logger.info(f"Collection '{collection_name}' already exists.")
        except (UnexpectedResponse, Exception):
            logger.info(f"Creating vector collection '{collection_name}' with size {vector_size}...")
            client.create_collection(
                collection_name=collection_name,
                vectors_config=qmodels.VectorParams(
                    size=vector_size,
                    distance=qmodels.Distance.COSINE
                )
            )

    @classmethod
    def index_chunks(cls, collection_name: str, chunks: List[Dict[str, Any]]):
        """
        Index multiple text chunks with their embedding vectors.
        chunks schema: List of { "id": str, "vector": List[float], "payload": Dict[str, Any] }
        """
        client = cls.get_client()
        # Verify collection exists first
        cls.ensure_collection(collection_name)
        
        points = []
        for c in chunks:
            points.append(
                qmodels.PointStruct(
                    id=c["id"],
                    vector=c["vector"],
                    payload=c["payload"]
                )
            )
            
        if points:
            client.upsert(
                collection_name=collection_name,
                points=points
            )
            logger.info(f"Indexed {len(points)} chunks into '{collection_name}'.")

    @classmethod
    def search(cls, collection_name: str, query_vector: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        """
        Perform vector semantic similarity search.
        Returns list of matching chunks with similarity scores and payloads.
        """
        client = cls.get_client()
        try:
            # Ensure collection exists before querying
            cls.ensure_collection(collection_name)
            
            results = client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=limit
            )
            
            retrieved = []
            for r in results:
                retrieved.append({
                    "id": r.id,
                    "score": r.score,
                    "payload": r.payload
                })
            return retrieved
        except Exception as e:
            logger.error(f"Search query failed on collection '{collection_name}': {str(e)}")
            return []
            
    @classmethod
    def delete_collection(cls, collection_name: str):
        """
        Delete a collection from vector store.
        """
        client = cls.get_client()
        try:
            client.delete_collection(collection_name)
            logger.info(f"Deleted collection '{collection_name}'.")
        except Exception as e:
            logger.error(f"Failed to delete collection '{collection_name}': {str(e)}")
