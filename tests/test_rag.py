from app.services.rag_service import rag_service


def test_rag_retrieval():
    ctx = rag_service.retrieve_context("Cold chain monitoring sensor log", top_k=2)
    assert "query" in ctx
    assert "vector_evidence" in ctx
    assert "graph_evidence" in ctx
