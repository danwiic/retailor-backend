JD_MAX_CHARS = 6000

JD_MARKER_START = "<<<JOB_DESCRIPTION_START>>>"
JD_MARKER_END = "<<<JOB_DESCRIPTION_END>>>"


def sanitize_jd(raw: str) -> str:
    """Guardrail for untrusted JD input. Strips control chars, enforces length,
    and removes any marker strings the user might supply to break out of the
    delimited data block."""
    if not isinstance(raw, str):
        raise ValueError("job description must be text")
    stripped = raw.strip()
    if not stripped:
        raise ValueError("job description is empty")
    if len(stripped) > JD_MAX_CHARS:
        raise ValueError(f"job description exceeds {JD_MAX_CHARS} characters")
    clean = "".join(ch for ch in stripped if ch == "\n" or ch == "\t" or ord(ch) >= 32)
    clean = clean.replace(JD_MARKER_START, "").replace(JD_MARKER_END, "")
    return clean


def wrap_jd_as_data(jd: str) -> str:
    """Wrap the sanitized JD in delimiters. Put the result in a user-message,
    NEVER in the system prompt. Markers tell the model it is data, not instructions."""
    return f"{JD_MARKER_START}\n{jd}\n{JD_MARKER_END}"