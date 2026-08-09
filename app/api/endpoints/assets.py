from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db import models
from app.schemas.assets import AssetResponse

router = APIRouter()


@router.get("/assets", response_model=List[AssetResponse])
def get_assets(db: Session = Depends(get_db)):
    assets = db.query(models.Asset).all()
    output = []
    for a in assets:
        meta_dict = {m.key: m.value for m in a.metadata_entries}
        output.append(AssetResponse(
            id=a.id,
            company_id=a.company_id,
            document_id=a.document_id,
            name=a.name,
            asset_type=a.asset_type,
            description=a.description,
            source_file=a.source_file,
            created_at=a.created_at.isoformat() if a.created_at else "",
            metadata=meta_dict
        ))
    return output


@router.get("/assets/{asset_id}", response_model=AssetResponse)
def get_asset(asset_id: str, db: Session = Depends(get_db)):
    asset = db.query(models.Asset).filter(models.Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail=f"Asset with ID '{asset_id}' not found.")

    meta_dict = {m.key: m.value for m in asset.metadata_entries}
    return AssetResponse(
        id=asset.id,
        company_id=asset.company_id,
        document_id=asset.document_id,
        name=asset.name,
        asset_type=asset.asset_type,
        description=asset.description,
        source_file=asset.source_file,
        created_at=asset.created_at.isoformat() if asset.created_at else "",
        metadata=meta_dict
    )
