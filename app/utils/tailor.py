import json
import logging
import os
import re

from app.schema import JDData, ResumeData

from .llm import bedrock, extract_text

logger = logging.getLogger(__name__)

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
- The tailored resume must not exceed the original resume's total word count by
  more than 10%.
- Reframing bullets for JD relevance must be achieved through rewording and
  reprioritizing existing content, not by adding new bullets or expanding
  bullets with additional detail.
- If a bullet becomes more detailed to match the JD, cut or shorten a
  less-relevant bullet elsewhere to stay within the word budget.
- Less relevant projects or experience for this specific JD should be condensed
  to fewer bullets, not just reworded at the same length.
- The summary is optional. Keep it to 2 lines maximum, approximately 35 words or
  fewer. It must do work the bullets cannot: state the candidate's years of
  experience and the specific JD-relevant framing in one concise line, with
  nothing else. If the resume does not support a concise, accurate summary with
  both elements, set summary to null and let the reordered/reframed bullets
  speak for themselves.
- Keep the final resume concise enough for one page, targeting approximately
  450-500 words maximum.
- No markdown, no explanation, no comments.
"""


CONDENSE_SYSTEM_PROMPT = """You are a professional resume editor.

Condense the supplied tailored resume to fit one page, targeting approximately
500 words maximum. Preserve all factual accuracy. Cut or merge the least
job-relevant bullets first, then shorten verbose bullets. Do not invent, remove,
or alter the candidate's name or contact information. Output ONLY valid JSON
matching the resume's shape exactly. No markdown, explanation, or comments.

The summary is optional and must be no more than approximately 35 words (about
2 lines). Keep it only if it accurately states the candidate's years of
experience and JD-relevant framing in one concise line. Otherwise set summary
to null.
"""


def _complete(system: str, payload: str, max_tokens: int = 4096) -> str:
    response = bedrock.converse(
        modelId=os.getenv("TAILOR_MODEL"),
        messages=[{"role": "user", "content": [{"text": payload}]}],
        system=[{"text": system}],
        inferenceConfig={"maxTokens": max_tokens},
    )
    return extract_text(response)


def _word_count(value: object) -> int:
    if isinstance(value, str):
        return len(re.findall(r"\b[\w'-]+\b", value))
    if isinstance(value, dict):
        return sum(_word_count(item) for item in value.values())
    if isinstance(value, list):
        return sum(_word_count(item) for item in value)
    return 0


def _word_budget(resume: ResumeData) -> int:
    original_words = _word_count(resume.model_dump())
    return min(500, max(1, int(original_words * 1.10 + 0.9999)))


def _fits_length_budget(resume: ResumeData, word_budget: int) -> bool:
    summary_words = _word_count(resume.summary) if resume.summary else 0
    return _word_count(resume.model_dump()) <= word_budget and summary_words <= 35


def _without_contact(resume: ResumeData) -> dict:
    return resume.model_copy(update={"contact": []}).model_dump()


def tailor_resume(resume: dict, jd: dict) -> dict:
    # Strip PII (contact block) before sending to the LLM; reattach unchanged after.
    validated_resume = ResumeData.model_validate(resume)
    validated_jd = JDData.model_validate(jd)
    contact = validated_resume.contact
    word_budget = _word_budget(validated_resume)
    resume_for_llm = validated_resume.model_copy(update={"contact": []})
    payload = json.dumps(
        {
            "resume": resume_for_llm.model_dump(),
            "job": validated_jd.model_dump(),
            "constraints": {
                "original_word_count": _word_count(validated_resume.model_dump()),
                "maximum_word_count": word_budget,
            },
        },
        indent=2,
    )

    result = ResumeData.model_validate_json(_complete(TAILOR_SYSTEM_PROMPT, payload))
    result.contact = contact
    if _fits_length_budget(result, word_budget):
        return result.model_dump()

    condensed_payload = json.dumps(
        {
            "resume": _without_contact(result),
            "job": validated_jd.model_dump(),
            "constraints": {
                "maximum_word_count": word_budget,
                "instruction": (
                    "Condense this resume to fit 1 page (~500 words) "
                    "while preserving all factual accuracy — cut or "
                    "merge the least JD-relevant bullets first. Keep "
                    "the summary to approximately 35 words or fewer, "
                    "or set it to null if it cannot state years of "
                    "experience and JD-relevant framing compactly."
                ),
            },
        },
        indent=2,
    )
    condensed = ResumeData.model_validate_json(
        _complete(CONDENSE_SYSTEM_PROMPT, condensed_payload)
    )
    condensed.contact = contact
    if _fits_length_budget(condensed, word_budget):
        return condensed.model_dump()
    raise RuntimeError("model exceeded the resume word budget")
