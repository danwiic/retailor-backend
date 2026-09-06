from fastapi import APIRouter, File, HTTPException, UploadFile

from app.utils.extract import extract_from_bytes
from app.utils.parse import parse_resume

router = APIRouter()

MAX_UPLOAD_BYTES = 5 * 1024 * 1024


@router.post("/parse")
async def parse_resume_file(file: UploadFile = File(...)):
    content = await file.read()
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="file too large")
    if not content:
        raise HTTPException(status_code=400, detail="empty file")
    try:
        raw_text = extract_from_bytes(content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    try:
        return parse_resume(raw_text)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"parsing failed: {e}")