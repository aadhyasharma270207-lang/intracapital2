import os
import shutil
import time
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend import config
from backend import scoring
from backend import models
from backend.services import ingestion_service
from backend.services import rag_service
from backend.services import granite_service
from backend.services import opportunity_service

# Check backend port availability from env variables
import socket
import sys

backend_host = os.getenv("BACKEND_HOST", "127.0.0.1")
try:
    backend_port = int(os.getenv("BACKEND_PORT", "8000"))
except ValueError:
    backend_port = 8000

def is_port_in_use(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            return False
        except OSError:
            return True

# Only verify if we are not running within a test suite (pytest/unittest)
is_test = "pytest" in sys.modules or "unittest" in sys.modules or os.getenv("TESTING") == "1"

if not is_test and is_port_in_use(backend_host, backend_port):
    print("=" * 60)
    print(f"❌ ERROR: Port {backend_port} is already in use on {backend_host}!")
    print("To resolve this, you can:")
    print("1. Kill the process occupying this port.")
    print("2. Set a different port using the BACKEND_PORT environment variable.")
    print("   Example: set BACKEND_PORT=8002")
    print("=" * 60)
    sys.exit(1)

# Initialize FastAPI App
app = FastAPI(
    title="INTRACAPITAL Backend API",
    description="Venture Discovery Engine API supporting ChromaDB, RAG, and IBM Granite",
    version="1.0.0"
)

# Enable CORS for frontend dashboard calls
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permits Streamlit requests from any port/host
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global runtime state for metrics tracking
_start_time = time.time()
_processing_time = 0.0

# Initialize Service singletons
granite_client = granite_service.GraniteService()
opportunity_manager = opportunity_service.OpportunityService()

# Helper for secure API token verification
def verify_api_key(x_api_key: Optional[str] = Header(None, alias="X-API-Key")):
    """
    Verifies the internal X-API-Key header token if configured.
    Bypasses authentication if FASTAPI_INTERNAL_API_KEY is not set in environment.
    """
    if config.FASTAPI_INTERNAL_API_KEY:
        if not x_api_key:
            raise HTTPException(
                status_code=401, 
                detail="Missing X-API-Key header."
            )
        if x_api_key != config.FASTAPI_INTERNAL_API_KEY:
            raise HTTPException(
                status_code=401, 
                detail="Unauthorized. Invalid X-API-Key."
            )

# ==========================================
# Endpoints
# ==========================================

@app.get("/")
def read_root():
    return {
        "application": "INTRACAPITAL",
        "status": "online",
        "mode": granite_client.mode_label
    }

@app.get("/health", response_model=models.HealthCheckResponse)
def health_check():
    """
    Polls subsystem states: RAG, ChromaDB, and IBM Granite.
    """
    rag_status = "online" if rag_service.CHROMADB_AVAILABLE else "offline"
    chromadb_status = "online"
    try:
        rag_service.get_collection()
    except Exception:
        chromadb_status = "offline"
        
    granite_status = "online" if granite_client.health_check() else "offline"
    
    return {
        "fastapi": "online",
        "rag": rag_status,
        "chromadb": chromadb_status,
        "granite": granite_status
    }

@app.post("/upload")
def upload_files(
    files: List[UploadFile] = File(...),
    dependencies: None = Depends(verify_api_key)
):
    """
    Uploads documents (PDF, TXT, CSV) into the uploads directory.
    """
    saved_files = []
    # Ensure directory is ready
    config.UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    
    for file in files:
        # Check supported files
        ext = Path(file.filename).suffix.lower()
        if ext not in [".txt", ".pdf", ".csv"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: {file.filename}. Only PDF, TXT, and CSV are permitted."
            )
            
        target_path = config.UPLOADS_DIR / file.filename
        try:
            with open(target_path, "wb") as f:
                f.write(file.file.read())
            
            size_kb = target_path.stat().st_size / 1024
            saved_files.append({
                "filename": file.filename,
                "file_type": ext.replace(".", ""),
                "size_kb": round(size_kb, 1),
                "status": "staged"
            })
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to write file {file.filename}: {str(e)}"
            )
            
    return {"status": "success", "files": saved_files}

@app.post("/analyze")
def analyze_documents(dependencies: None = Depends(verify_api_key)):
    """
    Triggers Ingestion, Chunking, and database indexing.
    """
    global _processing_time
    start_run = time.time()
    try:
        # Ingest directory
        chunks = ingestion_service.ingest_directory(config.UPLOADS_DIR)
        
        # Load into database
        if chunks:
            rag_service.initialize()
            rag_service.index_documents(chunks)
            
        _processing_time = round(time.time() - start_run, 2)
        return {
            "status": "success",
            "chunks_created": len(chunks),
            "processing_time_sec": _processing_time
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Analysis pipeline execution failed: {str(e)}"
        )

@app.post("/discover")
def discover_opportunities(dependencies: None = Depends(verify_api_key)):
    """
    Executes RAG retrieval, IBM Granite synthesis, scoring, and ranking.
    """
    global _processing_time
    start_run = time.time()
    try:
        # Query search keywords to fetch matching chunks
        queries = [
            "warehouse temperature problems and cold chain opportunities",
            "compressor failure and predictive maintenance assets",
            "logistics transit delays and route bottlenecks"
        ]
        
        evidence = []
        for q in queries:
            results = rag_service.retrieve_evidence(q, n_results=3)
            evidence.extend(results)
            
        # Deduplicate evidence chunks
        seen = set()
        unique_evidence = []
        for item in evidence:
            content_summary = item["text"][:100]
            if content_summary not in seen:
                seen.add(content_summary)
                unique_evidence.append(item)
                
        # Generate and score
        opportunities = opportunity_manager.discover_opportunities(unique_evidence)
        
        _processing_time += (time.time() - start_run)
        _processing_time = round(_processing_time, 2)
        
        return {
            "status": "success",
            "opportunities": opportunities,
            "evidence_used": unique_evidence
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Opportunity discovery failed: {str(e)}"
        )

@app.get("/opportunities", response_model=models.OpportunityListResponse)
def get_opportunities():
    """
    Fetches active venture discoveries.
    """
    opps = opportunity_manager.get_opportunities()
    return {"status": "success", "opportunities": opps}

@app.get("/opportunity/{opportunity_id}", response_model=models.OpportunityModel)
def get_opportunity(opportunity_id: str):
    """
    Fetches details of a single discovery.
    """
    opps = opportunity_manager.get_opportunities()
    for opp in opps:
        if opp.get("id") == opportunity_id:
            return opp
    raise HTTPException(status_code=404, detail="Opportunity not found.")

@app.post("/validate-opportunity", response_model=models.ValidationResponse)
def validate_opportunity(
    req: models.ValidationRequest,
    dependencies: None = Depends(verify_api_key)
):
    """
    Calculates adjusted overall scores dynamically based on user assumptions.
    Supports human-in-the-loop decision evaluation.
    """
    opps = opportunity_manager.get_opportunities()
    target_opp = None
    for opp in opps:
        if opp.get("id") == req.opportunity_id:
            target_opp = opp
            break
            
    # Fallback to match positionally or check default DEMO list if missing (recovers from server restarts)
    if not target_opp:
        for opp in opps:
            if req.opportunity_id in opp.get("id") or opp.get("id") in req.opportunity_id:
                target_opp = opp
                break
        if not target_opp:
            try:
                if "1" in req.opportunity_id or "cold" in req.opportunity_id:
                    target_opp = [o for o in opps if "1" in o.get("id") or "cold" in o.get("id").lower()][0]
                elif "2" in req.opportunity_id or "pred" in req.opportunity_id:
                    target_opp = [o for o in opps if "2" in o.get("id") or "pred" in o.get("id").lower()][0]
                elif "3" in req.opportunity_id or "risk" in req.opportunity_id:
                    target_opp = [o for o in opps if "3" in o.get("id") or "risk" in o.get("id").lower()][0]
            except Exception:
                pass
        if not target_opp:
            if opps:
                target_opp = opps[0]
            else:
                from backend.services.opportunity_service import DEMO_OPPORTUNITIES
                target_opp = DEMO_OPPORTUNITIES[0]
        
    # Calculate original score
    orig_score = target_opp.get("overall_score", 0.0)
    
    # Calculate adjusted score
    m = req.market_potential
    f = req.feasibility
    s = req.strategic_fit
    a = req.asset_reusability
    c = req.confidence
    
    adj_score = (m * 0.30) + (s * 0.25) + (f * 0.20) + (a * 0.15) + (c * 0.10)
    adj_score = round(adj_score, 1)
    
    diff = round(adj_score - orig_score, 1)
    
    explanation = (
        f"Adjusted Overall Score: {adj_score:.1f}/100. Breakdown:\n"
        f"- Market Potential (30%): {m:.1f}/100 (Contrib: {m * 0.30:.1f})\n"
        f"- Strategic Fit (25%): {s:.1f}/100 (Contrib: {s * 0.25:.1f})\n"
        f"- Feasibility (20%): {f:.1f}/100 (Contrib: {f * 0.20:.1f})\n"
        f"- Asset Reusability (15%): {a:.1f}/100 (Contrib: {a * 0.15:.1f})\n"
        f"- Confidence (10%): {c:.1f}/100 (Contrib: {c * 0.10:.1f})"
    )
    
    return {
        "opportunity_id": req.opportunity_id,
        "original_score": orig_score,
        "adjusted_score": adj_score,
        "difference": diff,
        "score_explanation": explanation
    }

@app.post("/expand-business-model", response_model=models.BusinessModelResponse)
def expand_business_model(
    req: models.BusinessModelRequest,
    dependencies: None = Depends(verify_api_key)
):
    """
    Expands an opportunity into a canvas business model.
    """
    canvas = opportunity_manager.generate_business_model(req.opportunity_id)
    return {
        "opportunity_id": req.opportunity_id,
        **canvas
    }

@app.post("/reset")
def reset_pipeline(dependencies: None = Depends(verify_api_key)):
    """
    Clears Vector database collection, upload folders, and opportunity state.
    """
    try:
        rag_service.clear_index()
        opportunity_manager.reset()
        
        # Clear uploads folder
        if config.UPLOADS_DIR.exists():
            shutil.rmtree(config.UPLOADS_DIR)
        config.UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
        
        return {"status": "success", "detail": "System environment reset complete."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reset operation failed: {str(e)}")

@app.get("/metrics", response_model=models.IngestionMetrics)
def get_metrics():
    """
    Computes corporate KPIs and system metrics.
    """
    opps = opportunity_manager.get_opportunities()
    
    # Files processed count
    file_count = 0
    if config.UPLOADS_DIR.exists():
        file_count = len([f for f in config.UPLOADS_DIR.iterdir() if f.is_file()])
        
    # Total chunks
    chunks_count = 0
    if rag_service.CHROMADB_AVAILABLE:
        try:
            coll = rag_service.get_collection()
            chunks_count = coll.count()
        except Exception:
            pass
            
    avg_conf = sum([o.get("confidence", 0.0) for o in opps]) / len(opps) if opps else 0.0
    top_score = opps[0].get("overall_score", 0.0) if opps else 0.0
    
    return {
        "documents_processed": file_count,
        "chunks": chunks_count,
        "opportunities": len(opps),
        "average_confidence": round(avg_conf, 1),
        "top_score": round(top_score, 1),
        "processing_time": _processing_time
    }

@app.get("/architecture")
def get_architecture():
    """
    Returns diagram data definitions.
    """
    return {
        "components": [
            {"id": "Company Data", "desc": "Raw operational assets (PDF, TXT, CSV Telemetry)."},
            {"id": "Streamlit", "desc": "Interactive, dark-themed user-facing client dashboard."},
            {"id": "FastAPI", "desc": "Server backend API orchestrating pipeline execution."},
            {"id": "Data Ingestion", "desc": "Segments documents, cleans text, and runs CSV anomaly detection."},
            {"id": "Embeddings", "desc": "Generates 384-dimensional local vectors using sentence-transformers."},
            {"id": "ChromaDB", "desc": "Persistent local vector database saving asset chunks."},
            {"id": "RAG", "desc": "Retrieves semantic evidence context for business query parameters."},
            {"id": "IBM Granite", "desc": "IBM's watsonx.ai foundation model synthesizing opportunities from evidence."},
            {"id": "Opportunity Engine", "desc": "Schedules execution, filters qualities, and formats outputs."},
            {"id": "Transparent Scoring", "desc": "Weighted mathematical score algorithm processed in Python."}
        ]
    }

@app.post("/load-demo-data")
def api_load_demo_data(dependencies: None = Depends(verify_api_key)):
    """
    Loads preconfigured files from data/sample_company/ to uploads/
    """
    try:
        if config.UPLOADS_DIR.exists():
            shutil.rmtree(config.UPLOADS_DIR)
        config.UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
        
        demo_files = [f for f in config.DATA_DIR.iterdir() if f.is_file()]
        for f in demo_files:
            shutil.copy(f, config.UPLOADS_DIR / f.name)
            
        return {"status": "success", "detail": f"Loaded {len(demo_files)} files into staging uploads."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load demo data: {str(e)}")
