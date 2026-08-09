from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.schemas.schemas import ProcessingJobResponse
from app.db.repositories.repos import ProcessingJobRepository
from app.db.sqlite import get_db, SessionLocal
from app.services.demo_service import DemoService

router = APIRouter()

def run_demo_load_task(job_id: str):
    """
    Background worker thread function to execute demo data ingestion.
    """
    db = SessionLocal()
    try:
        DemoService.load_demo_data(db, job_id)
    finally:
        db.close()

@router.post("/demo/load", response_model=ProcessingJobResponse, tags=["Demo"])
def load_demo(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Triggers loading the FrostLink Logistics fictional enterprise demo dataset.
    This creates files, builds graph relationships, chunks text, and inserts opportunities.
    """
    # Create the background job tracker
    job = ProcessingJobRepository.create(
        db=db,
        company_id="demo_company",
        job_type="discovery",
        status="running",
        current_step="01 Understanding Assets",
        progress=10.0
    )

    # Dispatch task to background pool
    background_tasks.add_task(run_demo_load_task, job_id=job.id)

    return job
