import shutil
from pathlib import Path
from backend import config

try:
    import chromadb
    from chromadb.utils import embedding_functions
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

COLLECTION_NAME = "intracapital_assets_v2"
_client = None
_emb_fn = None

def initialize():
    """
    Initializes ChromaDB persistent client and sentence-transformers functions.
    """
    global _client, _emb_fn
    if not CHROMADB_AVAILABLE:
        print("[RAG SERVICE] ChromaDB library not available.")
        return
        
    try:
        if _client is None:
            _client = chromadb.PersistentClient(path=str(config.VECTORSTORE_DIR))
        if _emb_fn is None:
            _emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        print("[RAG SERVICE] ChromaDB initialized successfully.")
    except Exception as e:
        print(f"[RAG SERVICE] Error during initialization: {e}")

def get_collection():
    """
    Safely retrieves or creates the vector collection.
    """
    global _client, _emb_fn
    if _client is None or _emb_fn is None:
        initialize()
        
    if _client is None:
        raise ImportError("ChromaDB is not initialized.")
        
    return _client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=_emb_fn
    )

def clear_index():
    """
    Clears all indices and cleans cache directories.
    """
    global _client
    print("[RAG SERVICE] Clearing vector database...")
    try:
        if _client is not None:
            try:
                _client.delete_collection(COLLECTION_NAME)
            except Exception:
                pass
                
        if config.VECTORSTORE_DIR.exists():
            shutil.rmtree(config.VECTORSTORE_DIR)
            config.VECTORSTORE_DIR.mkdir(parents=True, exist_ok=True)
            
        _client = None
        print("[RAG SERVICE] Vector store cleared successfully.")
    except Exception as e:
        print(f"[RAG SERVICE] Error clearing index: {e}")

def index_documents(chunks: list):
    """
    Adds a list of chunks into the ChromaDB collection.
    """
    if not CHROMADB_AVAILABLE:
        return
        
    if not chunks:
        return
        
    try:
        collection = get_collection()
        
        documents = []
        metadatas = []
        ids = []
        
        for idx, chunk in enumerate(chunks):
            documents.append(chunk["text"])
            
            meta = {
                "source": chunk.get("source", "unknown"),
                "filename": chunk.get("filename", "unknown"),
                "file_type": chunk.get("file_type", "unknown"),
                "chunk_id": chunk.get("chunk_id", str(idx))
            }
            if chunk.get("page") is not None:
                meta["page"] = chunk["page"]
                
            metadatas.append(meta)
            ids.append(f"c_{chunk.get('filename', 'doc')}_{idx}_{uuid_hash(chunk['text'])}")
            
        # Write in batches
        batch_size = 350
        for i in range(0, len(documents), batch_size):
            end_idx = min(i + batch_size, len(documents))
            collection.add(
                documents=documents[i:end_idx],
                metadatas=metadatas[i:end_idx],
                ids=ids[i:end_idx]
            )
        print(f"[RAG SERVICE] Indexed {len(documents)} document chunks in database.")
    except Exception as e:
        print(f"[RAG SERVICE] Indexing failed: {e}")
        raise e

def uuid_hash(text: str) -> str:
    """
    Generates a deterministic short hash from string context.
    """
    import hashlib
    return hashlib.md5(text.encode("utf-8", errors="ignore")).hexdigest()[:8]

def retrieve_evidence(query: str, n_results: int = 5) -> list:
    """
    Retrieves chunks matching query, returning source, page, filename, text, and relevance.
    """
    if not CHROMADB_AVAILABLE:
        return []
        
    try:
        collection = get_collection()
        results = collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        retrieved_items = []
        if results and "documents" in results and results["documents"]:
            docs = results["documents"][0]
            metas = results["metadatas"][0]
            # ChromaDB returns distances (lower is closer/better)
            distances = results.get("distances", [[0.5] * len(docs)])[0]
            
            for doc, meta, dist in zip(docs, metas, distances):
                # Convert distance to a human-readable relevance score (0-100%)
                # Normal cosine distance is 0 to 2 (for L2) or 0 to 1 (cosine). Let's map it safely.
                relevance = round(max(0.0, min(100.0, (1.0 - float(dist)) * 100.0)), 1)
                
                retrieved_items.append({
                    "text": doc,
                    "source": meta.get("source", "unknown"),
                    "filename": meta.get("filename", "unknown"),
                    "file_type": meta.get("file_type", "unknown"),
                    "page": meta.get("page"),
                    "chunk_id": meta.get("chunk_id", "unknown"),
                    "relevance": relevance
                })
        return retrieved_items
    except Exception as e:
        print(f"[RAG SERVICE] Search query failed: {e}")
        return []
