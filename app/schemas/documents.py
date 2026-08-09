from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any, List


class DocumentUploadResponse(BaseModel):
    document_id: str
    file_name: str
    file_type: str
    asset_type: str
    company_name: str
    chunk_count: int
    status: str
    message: str


class DocumentResponse(BaseModel):
    id: str
    company_id: str
    file_name: str
    file_type: str
    asset_type: str
    status: str
    chunk_count: int
    created_at: str

    model_config = ConfigDict(from_attributes=True)
