from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.schemas.schemas import ProcessingJobResponse
from app.db.repositories.repos import ProcessingJobRepository, CompanyRepository
from app.db.sqlite import get_db
from app.workflows.discovery_graph import DiscoveryWorkflow

router = APIRouter()

@router.post("/discovery/start", response_model=ProcessingJobResponse, tags=["Discovery"])
def start_discovery(
    company_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Spawns a background worker job to analyze company assets, run agent workflows,
    generate and evaluate business opportunities, and index logs.
    """
    company = CompanyRepository.get_by_id(db, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company workspace does not exist.")

    # Create new background process tracker
    job = ProcessingJobRepository.create(
        db=db,
        company_id=company_id,
        job_type="discovery",
        status="running",
        current_step="01 Understanding Assets",
        progress=10.0
    )

    # Queue background processing execution
    background_tasks.add_task(
        DiscoveryWorkflow.run_discovery,
        company_id=company_id,
        job_id=job.id
    )

    return job

@router.get("/discovery/{job_id}", response_model=ProcessingJobResponse, tags=["Discovery"])
def get_discovery_status(job_id: str, db: Session = Depends(get_db)):
    """
    Get current progress state of a queued discovery job.
    """
    job = ProcessingJobRepository.get_by_id(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Discovery job not found.")
    return job
