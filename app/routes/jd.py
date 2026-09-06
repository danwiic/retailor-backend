from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.utils.guardrails import sanitize_jd, wrap_jd_as_data
from app.utils.parse import parse_jd

router = APIRouter()


class JDPayload(BaseModel):
    text: str


@router.post("/analyze-jd")
async def analyze_jd(payload: JDPayload):
    try:
        clean = sanitize_jd(payload.text)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    wrapped = wrap_jd_as_data(clean)
    try:
        return parse_jd(wrapped)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"JD parsing failed: {e}")