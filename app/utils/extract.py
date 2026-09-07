from __future__ import annotations

import io
import zipfile


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

        try:
            with zipfile.ZipFile(io.BytesIO(content)) as archive:
                if "[Content_Types].xml" not in archive.namelist() or "word/document.xml" not in archive.namelist():
                    raise ValueError("unsupported file type")
            doc = Document(io.BytesIO(content))
        except (ValueError, zipfile.BadZipFile, KeyError) as e:
            raise ValueError("invalid DOCX file") from e
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    if kind == "pdf":
        import pdfplumber

        try:
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                if len(pdf.pages) > 20:
                    raise ValueError("PDF has too many pages")
                return "\n".join(page.extract_text() or "" for page in pdf.pages)
        except ValueError:
            raise
        except Exception as e:
            raise ValueError("invalid PDF file") from e
    raise ValueError("unsupported file type")


def extract_text(path: str) -> str:
    with open(path, "rb") as f:
        return extract_from_bytes(f.read())
