import io
import os
from datetime import datetime, timezone

import boto3
from docx import Document

BUCKET = os.getenv("S3_BUCKET", "resume-tailor-exports")

EXPORT_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def build_docx(resume: dict) -> bytes:
    doc = Document()

    doc.add_heading(resume.get("name", "Resume"), level=0)

    contact = resume.get("contact") or []
    contact_line = "  |  ".join(c.get("value", "") for c in contact if c.get("value"))
    if contact_line:
        doc.add_paragraph(contact_line)

    summary = resume.get("summary")
    if summary:
        doc.add_heading("Summary", level=1)
        doc.add_paragraph(summary)

    skills = resume.get("skills")
    if skills:
        doc.add_heading("Skills", level=1)
        doc.add_paragraph(", ".join(skills))

    def add_entries(heading, items):
        items = items or []
        if not items:
            return
        doc.add_heading(heading, level=1)
        for item in items:
            title = item.get("title") or item.get("name", "")
            company = item.get("company", "")
            dates = item.get("dates", "")
            header = " • ".join(x for x in [title, company, dates] if x)
            if header:
                doc.add_paragraph(header)
            for bullet in item.get("bullets") or []:
                doc.add_paragraph(bullet, style="List Bullet")

    add_entries("Experience", resume.get("experience"))
    add_entries("Projects", resume.get("projects"))

    education = resume.get("education")
    if education:
        doc.add_heading("Education", level=1)
        for item in education:
            school = item.get("school", "")
            degree = item.get("degree", "")
            dates = item.get("dates", "")
            line = " • ".join(x for x in [school, degree, dates] if x)
            if line:
                doc.add_paragraph(line)

    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def _s3_client():
    return boto3.client(
        "s3",
        region_name=os.getenv("AWS_REGION", "us-east-1"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )


def upload_export_and_sign(content: bytes, key: str) -> str:
    """Upload the DOCX to S3 and return a short-lived pre-signed download URL."""
    s3 = _s3_client()
    s3.put_object(Bucket=BUCKET, Key=key, Body=content, ContentType=EXPORT_MIME)
    url = s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": BUCKET, "Key": key},
        ExpiresIn=int(os.getenv("SIGNED_URL_TTL", "300")),
    )
    return url


def export_key(job_id: str) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"{job_id}/{ts}_tailored.docx"