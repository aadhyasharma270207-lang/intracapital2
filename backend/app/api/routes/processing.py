from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.schemas import ProcessingJobResponse
from app.db.repositories.repos import ProcessingJobRepository
from app.db.sqlite import get_db

router = APIRouter()

@router.get("/processing/{job_id}", response_model=ProcessingJobResponse, tags=["Processing"])
def get_processing_status(job_id: str, db: Session = Depends(get_db)):
    """
    Retrieves the execution status and step log trace for a background processing job.
    """
    job = ProcessingJobRepository.get_by_id(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Processing job not found.")
    return job
