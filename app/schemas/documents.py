from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from enum import Enum
from fastapi import UploadFile

class VisibilityEnum(str, Enum):
    private = "private"
    public =  "public"

class DocumentCreate(BaseModel):
    file: UploadFile
    visibility: VisibilityEnum

class DocumentResponse(BaseModel):
    id: int
    filename: str
    visibility: VisibilityEnum

    model_config = ConfigDict(from_attributes =True)

class DocumentDetail(DocumentResponse):
    created_at: datetime

class DocumentList(BaseModel):
    documents: list[DocumentResponse]

class DocumentsRequest(BaseModel):
    doc_id: int

class VisibilityChange(BaseModel):
    doc_id: int
    visibility: VisibilityEnum