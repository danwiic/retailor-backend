from fastapi import APIRouter, Header, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field
from starlette.concurrency import run_in_threadpool

from app.utils.guardrails import sanitize_jd, wrap_jd_as_data
from app.utils.parse import parse_jd
from app.utils.rates import check_limit

import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class JDPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")
    text: str = Field(min_length=1, max_length=6000)


@router.post("/analyze-jd")
async def analyze_jd(payload: JDPayload, request: Request, x_device_id: str = Header(default="")):
    try:
        clean = sanitize_jd(payload.text)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    wrapped = wrap_jd_as_data(clean)
    ip = request.client.host if request.client else "unknown"
    try:
        allowed = await run_in_threadpool(check_limit, ip, x_device_id, "analyze_jd")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError:
        raise HTTPException(status_code=503, detail="rate limiter is not configured")
    if not allowed:
        raise HTTPException(status_code=429, detail="daily JD analysis limit reached")
    try:
        return await run_in_threadpool(parse_jd, wrapped)
    except Exception:
        logger.exception("JD parsing failed")
        raise HTTPException(status_code=502, detail="JD parsing service temporarily unavailable")
