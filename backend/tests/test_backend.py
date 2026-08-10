import os
os.environ["DATABASE_URL"] = "sqlite:///./test_intracapital.db"
import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Adjust path to import backend modules
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.main import app
from app.db.sqlite import SessionLocal, Base, engine
from app.db.repositories.repos import CompanyRepository, AssetRepository, OpportunityRepository, ProcessingJobRepository
from app.services.embeddings_service import EmbeddingsService
from app.services.ingestion_service import IngestionService
from app.services.ollama_service import OllamaService
from app.services.graph_service import GraphService

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    """
    Sets up a temporary SQLite database schema for tests.
    """
    Base.metadata.create_all(bind=engine)
    yield
    # We clean up tables after test run
    Base.metadata.drop_all(bind=engine)


def test_api_health():
    """
    Test the basic API health status router.
    """
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "timestamp" in data


def test_system_status():
    """
    Test system health integration reporting.
    """
    response = client.get("/api/system/status")
    assert response.status_code == 200
    data = response.json()
    assert "fastapi" in data
    assert "sqlite" in data
    assert "ollama" in data
    assert "qdrant" in data
    assert "neo4j" in data
    assert data["fastapi"]["status"] == "ONLINE"


def test_embeddings_service():
    """
    Test embeddings generation. Must return a 384 dimensional vector
    regardless of local packages installation.
    """
    vector = EmbeddingsService.get_embedding("Test cargo operations and sensor data")
    assert isinstance(vector, list)
    assert len(vector) == 384
    assert all(isinstance(x, float) for x in vector)


def test_ingestion_chunking():
    """
    Test text chunker splitting logic.
    """
    sample_text = "This is a sentence. " * 100 # ~1900 chars
    chunks = IngestionService.chunk_text(sample_text, chunk_size=1000, overlap=200)
    assert len(chunks) >= 2
    assert len(chunks[0]) <= 1000


def test_db_repositories():
    """
    Verify SQLite ORM Repository operations (Company, Asset, Job creation).
    """
    db = SessionLocal()
    try:
        # Create company
        company = CompanyRepository.create(db, name="Test Ventures Inc", description="Test operations")
        assert company.id is not None
        assert company.name == "Test Ventures Inc"

        # Create asset
        asset = AssetRepository.create(
            db=db,
            company_id=company.id,
            file_name="ops_log.txt",
            asset_type="TXT",
            content="Testing asset content",
            metadata_json={"source": "pytest"}
        )
        assert asset.id is not None
        assert asset.status == "pending"

        # Update status
        AssetRepository.update_status(db, asset.id, "processed")
        db.refresh(asset)
        assert asset.status == "processed"

        # Create processing job
        job = ProcessingJobRepository.create(
            db=db,
            company_id=company.id,
            job_type="discovery",
            current_step="Pending",
            progress=0.0
        )
        assert job.id is not None
        assert job.status == "running"
        
        # Update job progress
        ProcessingJobRepository.update(db, job.id, progress=50.0, status="running")
        db.refresh(job)
        assert job.progress == 50.0

    finally:
        db.close()


def test_human_validator_score_recalculation():
    """
    Verify that manually updating criteria scores triggers the correct
    weighted average recalculation in the backend.
    """
    db = SessionLocal()
    try:
        company = CompanyRepository.create(db, name="Audit Co", description="Testing scoring formulas")
        
        opp = OpportunityRepository.create(
            db=db,
            company_id=company.id,
            title="SaaS Intelligence",
            short_description="Mock descriptions",
            problem="Mock problem",
            solution="Mock solution",
            target_customers="Enterprise",
            industry="IT",
            business_model="SaaS",
            revenue_model="Sub",
            market_potential=80.0,
            feasibility=80.0,
            strategic_fit=80.0,
            asset_reusability=80.0,
            confidence=80.0,
            overall_score=80.0
        )

        # Trigger validator endpoint manually
        payload = {
            "market_potential": 90.0,
            "feasibility": 70.0,
            "strategic_fit": 80.0,
            "asset_reusability": 60.0,
            "confidence": 50.0,
            "comments": "Adjusted feasibility and reusability due to high engineering costs",
            "status": "Under Review"
        }
        
        response = client.post(f"/api/opportunities/{opp.id}/validate", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        # Verify calculation:
        # (90 * 0.25) + (70 * 0.25) + (80 * 0.20) + (60 * 0.15) + (50 * 0.15)
        # = 22.5 + 17.5 + 16.0 + 9.0 + 7.5 = 72.5
        assert data["overall_score"] == 72.5
        assert data["status"] == "Under Review"
        
    finally:
        db.close()


def test_demo_load_endpoint():
    """
    Verify the demo load triggers a background job processing trace successfully.
    """
    response = client.post("/api/demo/load")
    assert response.status_code == 200
    data = response.json()
    assert data["job_type"] == "discovery"
    assert data["status"] == "running"
    assert data["company_id"] != ""
    assert "id" in data
