import uuid

from fastapi import APIRouter, Header, HTTPException, Request
from pydantic import BaseModel, ConfigDict
from starlette.concurrency import run_in_threadpool

from app.schema import JDData, ResumeData
from app.utils.export import build_docx, export_key, upload_export_and_sign
from app.utils.rates import check_tailor_limit
from app.utils.tailor import tailor_resume

router = APIRouter()

MAX_TAILOR_BODY_BYTES = 200 * 1024


class TailorRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    resume: ResumeData
    jd: JDData


@router.post("/tailor")
async def tailor(
    payload: TailorRequest,
    request: Request,
    x_device_id: str = Header(default=""),
):
    try:
        raw_len = int(request.headers.get("content-length") or 0)
    except ValueError:
        raw_len = 0
    if raw_len > MAX_TAILOR_BODY_BYTES:
        raise HTTPException(status_code=413, detail="request too large")

    ip = request.client.host if request.client else "unknown"
    try:
        allowed = await run_in_threadpool(check_tailor_limit, ip, x_device_id, "tailor")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError:
        raise HTTPException(status_code=503, detail="rate limiter is not configured")
    if not allowed:
        raise HTTPException(status_code=429, detail="daily tailor limit reached")

    job_id = uuid.uuid4().hex
    try:
        tailored = await run_in_threadpool(
            tailor_resume, payload.resume.model_dump(), payload.jd.model_dump()
        )
    except Exception:
        raise HTTPException(status_code=502, detail="tailoring service temporarily unavailable")

    try:
        docx_bytes = await run_in_threadpool(build_docx, tailored)
        url = await run_in_threadpool(
            upload_export_and_sign, docx_bytes, export_key(job_id)
        )
    except Exception:
        raise HTTPException(status_code=502, detail="export service temporarily unavailable")

    return {"tailored_resume": tailored, "download_url": url}
