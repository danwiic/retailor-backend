# Retailor

Resume Tailor MVP — upload a resume, paste a job description, get a tailored resume back as a DOCX.

## Pipeline

```
upload resume ──> extract text ──> LLM parse to JSON ──> user reviews/edits
                                                          │
JD paste ──> sanitize (guardrail) ──> LLM parse to requirements ──┘
                                                          │
                                                     /tailor ──> tailored JSON + DOCX
                                                                        │
                                                               S3 pre-signed URL
```

Two LLM steps, deliberately split:
- **Parse** (default `deepseek-v4-flash`): resume text → structured JSON, JD → requirements. Cheap, fast, can be revisited.
- **Tailor** (default `claude-opus-5`): rewrite the resume against the JD requirements. This is the expensive, rate-limited step.

## Stack

- FastAPI backend (Python 3.14)
- Neon (Postgres) for structured data — *planned*
- S3 for generated export files only (private bucket, pre-signed URLs) — *needs config*
- LLM via AgentRouter gateway (Anthropic-compatible API)

## Setup

```bash
py -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### Environment variables

Copy to `.env`:

```env
AGENT_ROUTER_API_KEY=...
AGENT_ROUTER_URL=https://agentrouter.org
APP_ENV=development
DATABASE_URL=postgresql://user:password@host/database?sslmode=require
PARSE_MODEL=deepseek-v4-flash
TAILOR_MODEL=claude-opus-5
PARSE_DAILY_LIMIT=5
JD_DAILY_LIMIT=5
TAILOR_DAILY_LIMIT=3
# Export (S3) — omit locally to test the pipeline without it
S3_BUCKET=resume-tailor-exports
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1
SIGNED_URL_TTL=300
```

## Run

```bash
py -m uvicorn app.main:app --reload --port 8000
```

Interactive docs at `http://localhost:8000/docs`.

In Neon, run `migrations/001_rate_limit_counters.sql` once before setting
`APP_ENV=production`. Production requires `DATABASE_URL` and a valid
`x-device-id` header on all LLM-backed endpoints. The rate-limit key is the
client IP plus device ID, with separate daily counters for parsing, JD
analysis, and tailoring.

## Endpoints

| Method | Path          | Body                                        | Returns                              |
|--------|---------------|---------------------------------------------|--------------------------------------|
| POST   | `/parse`      | multipart file (PDF/DOCX, ≤5MB)             | parsed resume JSON                   |
| POST   | `/analyze-jd` | `{"text": "<job posting>"}`                 | parsed JD requirements JSON          |
| POST   | `/tailor`     | `{"resume": {...}, "jd": {...}, "export_format": "docx"}` | `{"tailored_resume": {...}, "download_url": "...", "download_format": "docx"}` |

## Project layout

```
app/
  main.py              # FastAPI app + router registration
  schema.py            # RESUME_TEMPLATE, JD_TEMPLATE (LLM output contracts)
  utils/
    extract.py         # file → plain text (sniff magic bytes; DOCX/PDF)
    parse.py           # resume/JD → JSON via LLM
    tailor.py          # resume + JD → tailored resume via LLM
    guardrails.py      # sanitize_jd / wrap_jd_as_data (prompt-injection defense)
    llm.py             # shared Anthropic client
    export.py          # build_docx, upload to S3, pre-signed URL
  routes/
    upload.py          # POST /parse
    jd.py              # POST /analyze-jd
    tailor.py          # POST /tailor
```

## Security notes

- Magic-byte sniffing on upload — extension is not trusted; content is.
- JD input is sanitized (control chars, length cap) and wrapped in markers so it is treated as *data*, never as instructions.
- Contact/PII is stripped before the resume is sent to the tailoring LLM and reattached unchanged.
- S3 bucket is private; downloads use short-lived pre-signed URLs.
- LLM-backed endpoints are rate-limited per IP + device ID and action, with
  counters stored atomically in Postgres.
