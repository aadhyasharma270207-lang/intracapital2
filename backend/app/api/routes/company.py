from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.schemas import CompanyResponse, CompanyCreate
from app.db.repositories.repos import CompanyRepository
from app.db.sqlite import get_db

router = APIRouter()

@router.post("/company", response_model=CompanyResponse, tags=["Company"])
def create_company(company: CompanyCreate, db: Session = Depends(get_db)):
    """
    Creates a new company workspace registry.
    """
    try:
        new_company = CompanyRepository.create(db, company.name, company.description)
        return new_company
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/company/{company_id}", response_model=CompanyResponse, tags=["Company"])
def get_company(company_id: str, db: Session = Depends(get_db)):
    """
    Retrieves information on a specific company workspace.
    """
    company = CompanyRepository.get_by_id(db, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company workspace not found.")
    return company
