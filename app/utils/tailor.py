import json
import os

from app.schema import JDData, ResumeData

from .llm import client

TAILOR_SYSTEM_PROMPT = """You are a professional resume writer.

You receive:
1. A candidate's resume as JSON
2. A job description's parsed requirements as JSON

Rewrite the resume so it is tailored to the job. Keep it truthful — do not invent
experience, skills, or credentials the resume does not support. You may rephrase,
reemphasize, and reorder to highlight the most relevant points for this job.

Rules:
- Output ONLY valid JSON matching the resume's shape exactly.
- Never change the name or contact fields.
- Do not add fabrication. If the resume has gaps against the job's requirements,
  leave the content as-is rather than inventing.
- No markdown, no explanation, no comments.
"""


def tailor_resume(resume: dict, jd: dict) -> dict:
    # Strip PII (contact block) before sending to the LLM; reattach unchanged after.
    validated_resume = ResumeData.model_validate(resume)
    validated_jd = JDData.model_validate(jd)
    contact = validated_resume.contact
    resume_for_llm = validated_resume.model_copy(update={"contact": []})
    payload = json.dumps(
        {"resume": resume_for_llm.model_dump(), "job": validated_jd.model_dump()},
        indent=2,
    )
    msg = client.messages.create(
        model=os.getenv("TAILOR_MODEL"),
        max_tokens=2000,
        system=TAILOR_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": payload}],
    )
    for block in msg.content:
        if getattr(block, "type", "") == "text":
            result = ResumeData.model_validate_json(block.text)
            result.contact = contact
            return result.model_dump()
    raise RuntimeError("model returned no text block")
