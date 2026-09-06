import uuid
from typing import Any, Dict

from fastapi import APIRouter, Header, HTTPException, Request
from pydantic import BaseModel

from app.utils.export import build_docx, export_key, upload_export_and_sign
from app.utils.rates import check_tailor_limit
from app.utils.tailor import tailor_resume

router = APIRouter()

MAX_TAILOR_BODY_BYTES = 200 * 1024


class TailorRequest(BaseModel):
    resume: Dict[str, Any]
    jd: Dict[str, Any]


@router.post("/tailor")
async def tailor(
    payload: TailorRequest,
    request: Request,
    x_device_id: str = Header(default=""),
):
    raw_len = int(request.headers.get("content-length") or 0)
    if raw_len > MAX_TAILOR_BODY_BYTES:
        raise HTTPException(status_code=413, detail="request too large")

    ip = request.client.host if request.client else "unknown"
    if not check_tailor_limit(ip, x_device_id):
        raise HTTPException(status_code=429, detail="daily tailor limit reached")

    job_id = uuid.uuid4().hex
    try:
        tailored = tailor_resume(payload.resume, payload.jd)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"tailoring failed: {e}")

    try:
        docx_bytes = build_docx(tailored)
        url = upload_export_and_sign(docx_bytes, export_key(job_id))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"export failed: {e}")

    return {"tailored_resume": tailored, "download_url": url}