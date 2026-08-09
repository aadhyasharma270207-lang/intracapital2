import shutil
import os
import json
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from app.schemas.schemas import AssetResponse, AssetDetailResponse
from app.db.repositories.repos import AssetRepository, CompanyRepository
from app.db.sqlite import get_db
from app.core.config import settings
from app.services.ingestion_service import IngestionService
from app.services.embeddings_service import EmbeddingsService
from app.services.qdrant_service import QdrantService
from app.services.graph_service import GraphService

router = APIRouter()

@router.post("/assets/upload", response_model=AssetResponse, tags=["Assets"])
def upload_asset(
    company_id: str = Form(...),
    file: UploadFile = File(...),
    department: Optional[str] = Form(None),
    source: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Accepts document/table file, writes to directory, extracts contents, chunks,
    calculates vectors, index Qdrant collection and creates SQL trace records.
    """
    company = CompanyRepository.get_by_id(db, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company workspace does not exist.")

    # Validate file size if headers available
    # Max size calculation
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    
    # Save file on disk
    file_dir = settings.UPLOAD_DIR / company_id
    file_dir.mkdir(parents=True, exist_ok=True)
    file_path = file_dir / file.filename

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to write file to disk: {str(e)}")

    try:
        # Ingest and parse file
        parsed_data = IngestionService.parse_file(str(file_path), file.filename)
        
        # Save to database
        asset = AssetRepository.create(
            db=db,
            company_id=company_id,
            file_name=file.filename,
            asset_type=file.filename.split('.')[-1].upper(),
            department=department or parsed_data["metadata"].get("departments", [None])[0],
            source=source or "Upload Portal",
            metadata_json=parsed_data["metadata"],
            content=parsed_data["content"]
        )

        # Chunk, Embed, and Index
        chunks = IngestionService.chunk_text(parsed_data["content"])
        chunk_records = []

        for idx, text_val in enumerate(chunks):
            # Write chunk database entry
            db_chunk = AssetRepository.create_chunk(
                db=db,
                asset_id=asset.id,
                text=text_val,
                chunk_index=idx,
                metadata_json={"file_name": file.filename}
            )

            # Generate local vector embedding
            vector = EmbeddingsService.get_embedding(text_val)
            chunk_records.append({
                "id": db_chunk.id,
                "vector": vector,
                "payload": {
                    "asset_id": asset.id,
                    "chunk_id": db_chunk.id,
                    "file_name": file.filename,
                    "text": text_val
                }
            })

        # Store in Qdrant (collated under company namespaces)
        if chunk_records:
            QdrantService.index_chunks(collection_name=f"company_{company_id}", chunks=chunk_records)
            
        # Update asset status
        AssetRepository.update_status(db, asset.id, "processed")
        
        # Connect asset in knowledge graph
        GraphService.add_node(asset.id, "Asset", {"name": asset.file_name, "type": asset.asset_type})
        GraphService.add_relationship(company_id, asset.id, "OWNS")
        
        # Add basic signals relationships to graph
        for dept in parsed_data["metadata"].get("departments", []):
            GraphService.add_node(f"dept_{dept.lower()}", "Department", {"name": dept})
            GraphService.add_relationship(asset.id, f"dept_{dept.lower()}", "AFFECTS_DEPARTMENT")
            
        for tech in parsed_data["metadata"].get("technologies", []):
            GraphService.add_node(f"tech_{tech.lower()}", "Technology", {"name": tech})
            GraphService.add_relationship(asset.id, f"tech_{tech.lower()}", "MENTIONS_TECHNOLOGY")

        db.refresh(asset)
        
        # Prepare response schema values
        res = AssetResponse.model_validate(asset)
        res.chunks_count = len(chunks)
        return res

    except Exception as e:
        # Mark asset status as failed
        if 'asset' in locals() and asset:
            AssetRepository.update_status(db, asset.id, "failed")
        raise HTTPException(status_code=500, detail=f"Pipeline parsing error: {str(e)}")

@router.get("/assets", response_model=List[AssetResponse], tags=["Assets"])
def get_assets(company_id: Optional[str] = None, db: Session = Depends(get_db)):
    """
    List all uploaded company assets.
    """
    if company_id:
        assets = AssetRepository.get_by_company(db, company_id)
    else:
        assets = AssetRepository.get_all(db)
        
    response_list = []
    for asset in assets:
        chunks_count = len(AssetRepository.get_chunks_by_asset(db, asset.id))
        res = AssetResponse.model_validate(asset)
        res.chunks_count = chunks_count
        response_list.append(res)
        
    return response_list

@router.get("/assets/{asset_id}", response_model=AssetDetailResponse, tags=["Assets"])
def get_asset_detail(asset_id: str, db: Session = Depends(get_db)):
    """
    Retrieves full details of a specific asset including extracted text content.
    """
    asset = AssetRepository.get_by_id(db, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found.")
        
    chunks_count = len(AssetRepository.get_chunks_by_asset(db, asset.id))
    res = AssetDetailResponse.model_validate(asset)
    res.chunks_count = chunks_count
    return res

@router.delete("/assets/{asset_id}", tags=["Assets"])
def delete_asset(asset_id: str, db: Session = Depends(get_db)):
    """
    Deletes an asset from SQLite. (Vectors are ignored or handled in mock collections).
    """
    asset = AssetRepository.get_by_id(db, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found.")
        
    # Delete local physical file if exists
    file_path = settings.UPLOAD_DIR / asset.company_id / asset.file_name
    if file_path.exists():
        try:
            os.remove(file_path)
        except Exception:
            pass
            
    success = AssetRepository.delete(db, asset_id)
    if not success:
         raise HTTPException(status_code=500, detail="Failed to delete asset from database.")
         
    return {"status": "success", "message": f"Asset {asset_id} deleted successfully."}
