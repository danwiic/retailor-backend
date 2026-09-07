# Retailor Frontend API Contract

This document is the frontend integration contract for the current backend.
When the backend changes, update this document with the implementation.

## Base URL

Use an environment variable in the frontend:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Production should point to the deployed API origin, not the frontend origin.

## Device ID

Every LLM-backed request requires the header:

```http
x-device-id: <stable-client-generated-id>
```

Generate the ID once in the browser and persist it in local storage. Do not
generate a new ID for every request.

The backend validates IDs containing 1-128 letters, numbers, `_`, or `-`.

The device ID is used with the client IP for daily abuse prevention. It is not
authentication and must not be presented to the user as an account identity.

## `POST /parse`

Parses a PDF or DOCX resume into editable structured JSON.

Request:

```http
Content-Type: multipart/form-data
x-device-id: <device-id>
```

Multipart field:

```text
file: PDF or DOCX, maximum 5 MB
```

The backend checks actual file bytes, not only the filename extension. The
extracted text is also limited before it is sent to the LLM.

Response:

```json
{
  "name": "Jane Doe",
  "contact": [
    {
      "label": "email",
      "value": "jane@example.com"
    }
  ],
  "summary": "Backend engineer with API experience.",
  "skills": ["Python", "FastAPI"],
  "experience": [],
  "projects": [],
  "education": []
}
```

## `POST /analyze-jd`

Parses a job description into editable requirements.

Request:

```http
Content-Type: application/json
x-device-id: <device-id>
```

```json
{
  "text": "Full job description text..."
}
```

The text must be between 1 and 6,000 characters.

Response:

```json
{
  "title": "Backend Engineer",
  "company": "Example Corp",
  "location": "Remote",
  "employment_type": "Full-time",
  "requirements": [
    "Experience designing REST APIs"
  ],
  "nice_to_have": [],
  "responsibilities": [
    "Design and maintain backend services"
  ]
}
```

## `POST /tailor`

Tailors the user-reviewed resume against the user-reviewed job description and
generates a DOCX export.

Request:

```http
Content-Type: application/json
x-device-id: <device-id>
```

```json
{
  "resume": {
    "name": "Jane Doe",
    "contact": [],
    "summary": "...",
    "skills": ["Python"],
    "experience": [],
    "projects": [],
    "education": []
  },
  "jd": {
    "title": "Backend Engineer",
    "company": "Example Corp",
    "location": "Remote",
    "employment_type": "Full-time",
    "requirements": ["Experience designing REST APIs"],
    "nice_to_have": [],
    "responsibilities": []
  }
}
```

Response:

```json
{
  "tailored_resume": {
    "name": "Jane Doe",
    "contact": [],
    "summary": "...",
    "skills": ["Python"],
    "experience": [],
    "projects": [],
    "education": []
  },
  "download_url": "https://temporary-signed-url..."
}
```

The frontend must send the edited resume and edited JD, not only the original
LLM responses. The download URL is short-lived and should be used promptly.

## `GET /health`

Response:

```json
{
  "status": "ok"
}
```

## Errors

The backend normally returns:

```json
{
  "detail": "human-readable message"
}
```

Interpret status codes as follows:

- `400`: invalid input or invalid device ID
- `413`: file, extracted text, or request too large
- `429`: daily limit reached
- `502`: LLM or export provider temporarily unavailable
- `503`: production rate limiter or database is unavailable

Frontend behavior:

- Show `400` messages near the relevant field or control.
- Show a file-specific message for `413` upload failures.
- Explain that the daily quota has been reached for `429`.
- Offer retry for `502` and `503`.
- Never display stack traces or raw provider errors.

## Current Daily Limits

These are configurable on the backend:

- Resume parsing: 5 requests per day by default
- JD analysis: 5 requests per day by default
- Tailoring: 3 requests per day by default

The frontend should not hardcode these values into business logic. It should
handle the `429` response and display the backend-provided explanation.
