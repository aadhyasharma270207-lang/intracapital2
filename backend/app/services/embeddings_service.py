import logging
import hashlib
from typing import List
from app.core.config import settings

logger = logging.getLogger(__name__)

# Try to import sentence-transformers, set flag if missing
HAS_SENTENCE_TRANSFORMERS = False
model_instance = None

try:
    from sentence_transformers import SentenceTransformer
    # We load standard lightweight model
    model_instance = SentenceTransformer("all-MiniLM-L6-v2")
    HAS_SENTENCE_TRANSFORMERS = True
    logger.info("SentenceTransformer loaded successfully.")
except Exception as e:
    logger.warning(f"SentenceTransformer not loaded (could be missing torch/sentence-transformers dependencies): {str(e)}. Falling back to deterministic mock embedding service.")

class EmbeddingsService:
    @staticmethod
    def get_embedding(text: str) -> List[float]:
        """
        Generate a 384-dimensional embedding vector for a given text segment.
        Uses sentence-transformers if available, else falls back to a deterministic mock vector.
        """
        if HAS_SENTENCE_TRANSFORMERS and model_instance is not None:
            try:
                embedding = model_instance.encode(text)
                return [float(x) for x in embedding]
            except Exception as e:
                logger.error(f"Failed to generate SentenceTransformer embedding: {str(e)}. Using fallback.")
        
        # Fallback: Deterministic mock vector generation (dimension 384)
        return EmbeddingsService._generate_mock_embedding(text)

    @staticmethod
    def _generate_mock_embedding(text: str) -> List[float]:
        """
        Generates a 384-dimensional vector derived from the sha256 hash of the input text.
        This provides deterministic embeddings for identical texts, enabling semantic mocks.
        """
        # Create a hash of the text
        hash_digest = hashlib.sha256(text.encode("utf-8")).digest()
        
        # Populate 384 dimensions using recurring slices of the hash
        vector = []
        for i in range(384):
            # Derive a float value between -1.0 and 1.0 from byte values
            byte_idx = (i * 7) % len(hash_digest)
            val = hash_digest[byte_idx]
            # Map [0, 255] to [-1.0, 1.0]
            norm_val = (val / 127.5) - 1.0
            # Add index-dependent fluctuation to ensure variations
            fluctuation = ((i % 17) - 8.0) / 40.0
            vector.append(max(-1.0, min(1.0, norm_val + fluctuation)))
            
        # Normalize vector (l2 norm)
        magnitude = sum(x*x for x in vector) ** 0.5
        if magnitude > 0:
            vector = [x / magnitude for x in vector]
            
        return vector
