import time
from pathlib import Path
from backend import config
from backend import scoring
from backend.services import ingestion_service
from backend.services import rag_service
from backend.services import opportunity_service

def run_pipeline(data_directory: str = None) -> dict:
    """
    Coordinates the full INTRACAPITAL discovery pipeline sequentially.
    Used for testing, background pipelines, and API triggers.
    """
    start_time = time.time()
    errors = []
    assets = []
    chunks_count = 0
    evidence = []
    opportunities = []
    
    target_dir = Path(data_directory) if data_directory else config.UPLOADS_DIR
    print(f"[PIPELINE] Starting runner on directory: {target_dir}")
    
    # 1. Ingestion Phase
    try:
        if not target_dir.exists():
            raise FileNotFoundError(f"Target directory {target_dir} not found.")
            
        file_entries = [f for f in target_dir.iterdir() if f.is_file() and f.suffix.lower() in [".txt", ".pdf", ".csv"]]
        assets = [f.name for f in file_entries]
        
        chunks = ingestion_service.ingest_directory(target_dir)
        chunks_count = len(chunks)
    except Exception as e:
        err = f"Ingestion error: {str(e)}"
        print(f"[PIPELINE] {err}")
        errors.append(err)
        chunks = []

    # 2. RAG Indexing Phase
    if chunks:
        try:
            rag_service.initialize()
            rag_service.index_documents(chunks)
        except Exception as e:
            err = f"RAG indexing error: {str(e)}"
            print(f"[PIPELINE] {err}")
            errors.append(err)
            
    # 3. Retrieval & Synthesis Phase
    try:
        queries = [
            "warehouse temperature problems and cold chain opportunities",
            "compressor failure and predictive maintenance assets",
            "logistics transit delays and route bottlenecks"
        ]
        
        raw_evidence = []
        if chunks and not any("RAG indexing error" in err for err in errors):
            for q in queries:
                raw_evidence.extend(rag_service.retrieve_evidence(q, n_results=3))
                
        # Deduplicate
        seen = set()
        for item in raw_evidence:
            summary = item["text"][:100]
            if summary not in seen:
                seen.add(summary)
                evidence.append(item)
                
        # Discover and rank
        manager = opportunity_service.OpportunityService()
        opportunities = manager.discover_opportunities(evidence)
        status = "DEMO_MODE" if manager.granite.mode_label == "🟡 DEMO MODE" else "LIVE_MODE"
    except Exception as e:
        err = f"Discovery engine error: {str(e)}"
        print(f"[PIPELINE] {err}")
        errors.append(err)
        status = "failed"
        
    processing_time = round(time.time() - start_time, 2)
    
    return {
        "status": status,
        "assets_processed": assets,
        "chunks_created": chunks_count,
        "retrieved_evidence": evidence,
        "opportunities": opportunities,
        "errors": errors,
        "processing_time": processing_time
    }

if __name__ == "__main__":
    res = run_pipeline(str(config.DATA_DIR))
    print("\n--- CLI Pipeline Run Finished ---")
    print(f"Status: {res['status']}")
    print(f"Opportunities Discovered: {len(res['opportunities'])}")
    for o in res["opportunities"]:
        print(f"- {o['name']} (Overall Score: {o.get('overall_score')}/100)")
