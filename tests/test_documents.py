import io


def test_document_upload(client):
    file_content = b"This is a test enterprise document containing sensor data for cold chain logistics."
    file_obj = io.BytesIO(file_content)

    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("test_doc.txt", file_obj, "text/plain")},
        data={"asset_type": "SENSOR_DATA", "company_name": "Test Company"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["file_name"] == "test_doc.txt"
    assert data["asset_type"] == "SENSOR_DATA"
    assert data["status"] == "processed"
    assert data["chunk_count"] > 0


def test_list_documents(client):
    response = client.get("/api/v1/documents")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
