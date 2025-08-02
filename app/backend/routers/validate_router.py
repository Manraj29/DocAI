from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import List
import os
from backend.services.validate_service import validate_document

router = APIRouter()

class ValidationRequest(BaseModel):
    text: str
    rules: list

@router.post("/")
async def validate_doc(request: ValidationRequest):
    try:
        valid_result = validate_document(request)
        return valid_result
    except Exception as e:
        return {"error": str(e)}
