from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any, List


class AssetMetadataSchema(BaseModel):
    key: str
    value: str

    model_config = ConfigDict(from_attributes=True)


class AssetResponse(BaseModel):
    id: str
    company_id: str
    document_id: Optional[str] = None
    name: str
    asset_type: str
    description: Optional[str] = None
    source_file: Optional[str] = None
    created_at: str
    metadata: Dict[str, Any] = {}

    model_config = ConfigDict(from_attributes=True)
