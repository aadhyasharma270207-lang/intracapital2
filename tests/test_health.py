def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["api"] == "ok"
    assert "ollama" in data
    assert "neo4j" in data
    assert "qdrant" in data
