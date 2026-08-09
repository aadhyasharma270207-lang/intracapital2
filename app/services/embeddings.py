from typing import List
from sentence_transformers import SentenceTransformer
from app.utils.logger import logger

_model = None

def get_embedding_model():
    global _model
    if _model is None:
        logger.info("[EMBEDDINGS] Initializing sentence-transformers model 'all-MiniLM-L6-v2'...")
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


class EmbeddingService:
    @staticmethod
    def generate_embedding(text: str) -> List[float]:
        model = get_embedding_model()
        vector = model.encode(text, convert_to_numpy=True).tolist()
        return vector

    @staticmethod
    def generate_embeddings(texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        model = get_embedding_model()
        vectors = model.encode(texts, convert_to_numpy=True).tolist()
        return vectors
