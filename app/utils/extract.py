from __future__ import annotations

import io


def sniff(b: bytes) -> str:
    if b.startswith(b"%PDF"):
        return "pdf"
    if b.startswith(b"PK"):
        return "docx"
    raise ValueError("unsupported file type")


def extract_from_bytes(content: bytes) -> str:
    kind = sniff(content)
    if kind == "docx":
        from docx import Document

        doc = Document(io.BytesIO(content))
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    if kind == "pdf":
        import pdfplumber

        with pdfplumber.open(io.BytesIO(content)) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    raise ValueError("unsupported file type")


def extract_text(path: str) -> str:
    with open(path, "rb") as f:
        return extract_from_bytes(f.read())