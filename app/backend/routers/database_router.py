from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from backend.database import insert_document

router = APIRouter()

class ImageItem(BaseModel):
    image_base64: str
    ocr_text: str
    corrected_text: str

class StorePayload(BaseModel):
    user_id: str
    filename: str
    type: Optional[str] = None
    content: str
    clean_content: str
    images: List[ImageItem]
    fields: Dict
    tables: Dict
    rules: Dict
    validation_status: Optional[str] = None
    validation_report: Dict
    failed_fields: Optional[List[str]] = None

@router.post("/")
def store_document(payload: StorePayload):
    try:
        inserted_id = insert_document(payload.dict())
        return {"success": True, "inserted_id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
