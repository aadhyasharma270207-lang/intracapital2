from fastapi import APIRouter

router = APIRouter()

@router.get("/architecture", tags=["Architecture"])
def get_architecture_diagram():
    """
    Returns structured layout nodes and flow directions representing the application's physical architecture.
    """
    return {
        "nodes": [
            {"id": "source", "label": "Enterprise Data Sources", "sublabel": "PDF, DOCX, CSV, IoT logs", "type": "input"},
            {"id": "prep", "label": "IBM Data Prep / Docling", "sublabel": "Clean, Chunk & Normalize", "type": "process"},
            {"id": "vector", "label": "Qdrant Vector DB", "sublabel": "Local Semantic Storage (384d)", "type": "storage"},
            {"id": "graph", "label": "Neo4j Knowledge Graph", "sublabel": "Relational Signals Connection", "type": "storage"},
            {"id": "rag", "label": "RAG Retrieval", "sublabel": "Hybrid Query Routing Context", "type": "retriever"},
            {"id": "agents", "label": "LangGraph Orchestrator", "sublabel": "Collaborative Agent Group", "type": "agent_group"},
            {"id": "granite", "label": "IBM Granite 4.x (Ollama)", "sublabel": "Local Inference Engine", "type": "llm"},
            {"id": "scoring", "label": "Venture Scoring Model", "sublabel": "Explainable Weighted Ranking", "type": "evaluator"},
            {"id": "output", "label": "Discovery Dashboard", "sublabel": "Human-in-the-Loop Validator", "type": "output"}
        ],
        "edges": [
            {"source": "source", "target": "prep", "label": "Ingest"},
            {"source": "prep", "target": "vector", "label": "Index Vectors"},
            {"source": "prep", "target": "graph", "label": "Map Relationships"},
            {"source": "vector", "target": "rag", "label": "Semantic Top-K"},
            {"source": "graph", "target": "rag", "label": "Connected Concepts"},
            {"source": "rag", "target": "agents", "label": "Context Enrichment"},
            {"source": "agents", "target": "granite", "label": "Structured Query"},
            {"source": "granite", "target": "scoring", "label": "Structured Plan"},
            {"source": "scoring", "target": "output", "label": "Rank & Explain"}
        ]
    }
