import os
import uuid
import shutil
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db import models
from app.schemas.documents import DocumentUploadResponse, DocumentResponse
from app.utils.taxonomy import AssetType
from app.utils.logger import logger
from app.services.doc_parser import DocumentParser
from app.services.qdrant_service import qdrant_service
from app.services.neo4j_service import neo4j_service

router = APIRouter()
UPLOAD_DIR = os.path.abspath("./uploaded_documents")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    asset_type: str = Form("OTHER"),
    company_name: str = Form("Intracapital Corp"),
    db: Session = Depends(get_db)
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename missing in upload.")

    # 1. Normalize company
    company = db.query(models.Company).filter(models.Company.name == company_name).first()
    if not company:
        company = models.Company(name=company_name, industry="General")
        db.add(company)
        db.commit()
        db.refresh(company)

    # 2. Save original file
    doc_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename)[1].lower()
    saved_filename = f"{doc_id}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, saved_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    norm_asset_type = AssetType.from_string(asset_type).value

    # 3. Create Document DB record
    db_doc = models.Document(
        id=doc_id,
        company_id=company.id,
        file_name=file.filename,
        file_type=ext.replace(".", "").upper(),
        file_path=file_path,
        asset_type=norm_asset_type,
        status="processing"
    )
    db.add(db_doc)

    # 4. Extract Asset entity
    asset_name = os.path.splitext(file.filename)[0].replace("_", " ").title()
    db_asset = models.Asset(
        company_id=company.id,
        document_id=doc_id,
        name=asset_name,
        asset_type=norm_asset_type,
        description=f"Enterprise asset extracted from {file.filename}",
        source_file=file.filename
    )
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)

    # 5. Parse and Chunk document
    try:
        chunks = DocumentParser.parse_file(
            file_path=file_path,
            document_id=doc_id,
            source_file=file.filename,
            asset_type=norm_asset_type,
            company=company_name
        )
    except Exception as e:
        logger.error(f"[UPLOAD] Failed to parse document: {e}")
        db_doc.status = "error"
        db.commit()
        raise HTTPException(status_code=500, detail=f"Failed to parse document: {str(e)}")

    chunk_dicts = [c.to_dict() for c in chunks]

    # 6. Store vectors in Qdrant
    qdrant_service.insert_chunks(chunk_dicts)

    # 7. Knowledge Graph Insertion in Neo4j
    company_node = neo4j_service.create_node("Company", {"id": company.id, "name": company.name})
    asset_node = neo4j_service.create_node(norm_asset_type.capitalize(), {
        "id": db_asset.id,
        "name": db_asset.name,
        "asset_type": norm_asset_type,
        "source_file": file.filename
    })
    neo4j_service.create_relationship("Company", company.id, "OWNS", norm_asset_type.capitalize(), db_asset.id)

    # Extract dynamic graph entities based on asset type
    if norm_asset_type in ["SENSOR_DATA", "MANUFACTURING_LOG"]:
        sensor_node = neo4j_service.create_node("Sensor", {"id": f"sensor-{db_asset.id[:8]}", "name": f"{asset_name} Sensor"})
        neo4j_service.create_relationship(norm_asset_type.capitalize(), db_asset.id, "MEASURES", "Sensor", f"sensor-{db_asset.id[:8]}")
    elif norm_asset_type in ["PATENT", "RESEARCH", "TECHNOLOGY"]:
        tech_node = neo4j_service.create_node("Technology", {"id": f"tech-{db_asset.id[:8]}", "name": f"{asset_name} Tech"})
        neo4j_service.create_relationship(norm_asset_type.capitalize(), db_asset.id, "CAN_ENABLE", "Technology", f"tech-{db_asset.id[:8]}")

    # 8. Update Document DB record
    db_doc.chunk_count = len(chunks)
    db_doc.status = "processed"
    db.commit()

    logger.info(f"[UPLOAD] Document '{file.filename}' processed successfully ({len(chunks)} chunks).")

    return DocumentUploadResponse(
        document_id=doc_id,
        file_name=file.filename,
        file_type=ext.replace(".", "").upper(),
        asset_type=norm_asset_type,
        company_name=company_name,
        chunk_count=len(chunks),
        status="processed",
        message="Document uploaded, chunked, vector-indexed in Qdrant, and mapped in Neo4j Knowledge Graph."
    )


@router.get("/documents", response_model=List[DocumentResponse])
def list_documents(db: Session = Depends(get_db)):
    docs = db.query(models.Document).all()
    output = []
    for d in docs:
        output.append(DocumentResponse(
            id=d.id,
            company_id=d.company_id,
            file_name=d.file_name,
            file_type=d.file_type,
            asset_type=d.asset_type,
            status=d.status,
            chunk_count=d.chunk_count or 0,
            created_at=d.created_at.isoformat() if d.created_at else ""
        ))
    return output
