from fastapi import APIRouter, File, UploadFile
from backend.services.document_service import process_document
from fastapi.responses import JSONResponse

router = APIRouter()

@router.post("/")
async def upload_document(file: UploadFile = File(...)):
    try:
        content = await file.read()
        result = process_document(content, file.filename)
        return result
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
