from fastapi import APIRouter, File, Header, HTTPException, Request, UploadFile
from starlette.concurrency import run_in_threadpool

from app.utils.extract import extract_from_bytes
from app.utils.parse import parse_resume
from app.utils.rates import check_limit

router = APIRouter()

MAX_UPLOAD_BYTES = 5 * 1024 * 1024
MAX_EXTRACTED_CHARS = 30000


@router.post("/parse")
async def parse_resume_file(
    request: Request,
    file: UploadFile = File(...),
    x_device_id: str = Header(default=""),
):
    try:
        content = await file.read(MAX_UPLOAD_BYTES + 1)
    except Exception:
        raise HTTPException(status_code=400, detail="could not read upload")
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="file too large")
    if not content:
        raise HTTPException(status_code=400, detail="empty file")
    try:
        raw_text = extract_from_bytes(content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if len(raw_text) > MAX_EXTRACTED_CHARS:
        raise HTTPException(status_code=413, detail="extracted resume text is too long")
    ip = request.client.host if request.client else "unknown"
    try:
        allowed = await run_in_threadpool(check_limit, ip, x_device_id, "parse")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError:
        raise HTTPException(status_code=503, detail="rate limiter is not configured")
    if not allowed:
        raise HTTPException(status_code=429, detail="daily parse limit reached")
    try:
        return await run_in_threadpool(parse_resume, raw_text)
    except Exception:
        raise HTTPException(status_code=502, detail="parsing service temporarily unavailable")
