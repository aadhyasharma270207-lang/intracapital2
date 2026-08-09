from app.services.qdrant_service import qdrant_service


def test_qdrant_indexing_and_search():
    chunks = [
        {
            "chunk_id": "c-001",
            "document_id": "doc-1",
            "source_file": "sensor.txt",
            "content": "Temperature sensor node TS-101 recorded overheating in Zone A warehouse.",
            "asset_type": "SENSOR_DATA",
            "company": "Test Enterprise",
            "page_number": 1,
            "section_title": "Logs",
            "timestamp": "2026-05-15T00:00:00Z"
        }
    ]

    success = qdrant_service.insert_chunks(chunks)
    assert success is True

    results = qdrant_service.search(query="overheating temperature sensor", top_k=1)
    assert len(results) >= 1
    assert "TS-101" in results[0]["content"]
