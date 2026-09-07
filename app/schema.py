from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


RESUME_TEMPLATE = {
    "name": "DAN RANIEL PIRANTE",
    "contact": [
        {"label": "email", "value": "danpirante9@gmail.com"},
        {"label": "phone", "value": "+63 9456182895"},
        {"label": "location", "value": "Cavite City, Cavite"},
        {"label": "website", "value": "www.danpirante.dev"},
    ],
    "summary": "Senior backend engineer...",
    "skills": ["React", "TypeScript", "FastAPI", "PostgreSQL", "Kubernetes"],
    "experience": [
        {
            "title": "Full Stack Developer Intern",
            "company": "S.P. Madrid & Associates Philippines",
            "dates": "Feb 2026 – June 2026",
            "bullets": ["Co-built a loan reminder...", "..."],
        }
    ],
    "projects": [
        {
            "name": "Bulk Email Blasting Platform",
            "dates": "Feb 2026 – June 2026",
            "bullets": ["Built a production bulk email...", "..."],
        }
    ],
    "education": [
        {
            "school": "Cavite State University – Cavite City Campus",
            "degree": "Bachelor of Science in Information Technology",
            "dates": "September 2022 – 2026",
            "location": "Cavite City, Cavite",
        }
    ],
}

JD_TEMPLATE = {
    "title": "Senior Backend Engineer",
    "company": "Example Corp",
    "location": "Remote",
    "employment_type": "Full-time",
    "requirements": [
        "5+ years of Python experience",
        "Experience designing REST APIs",
    ],
    "nice_to_have": ["Kubernetes experience"],
    "responsibilities": [
        "Design and maintain backend services",
        "Collaborate with cross-functional teams",
    ],
}


class ContactItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    label: str = Field(max_length=40)
    value: str = Field(max_length=300)


class ResumeEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str | None = Field(default=None, max_length=200)
    name: str | None = Field(default=None, max_length=200)
    company: str | None = Field(default=None, max_length=200)
    dates: str | None = Field(default=None, max_length=100)
    bullets: list[Annotated[str, Field(max_length=1000)]] = Field(default_factory=list, max_length=30)


class EducationEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")
    school: str = Field(default="", max_length=250)
    degree: str = Field(default="", max_length=250)
    dates: str = Field(default="", max_length=100)
    location: str | None = Field(default=None, max_length=200)


class ResumeData(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(default="", max_length=200)
    contact: list[ContactItem] = Field(default_factory=list, max_length=20)
    summary: str | None = Field(default=None, max_length=4000)
    skills: list[Annotated[str, Field(max_length=100)]] = Field(default_factory=list, max_length=100)
    experience: list[ResumeEntry] = Field(default_factory=list, max_length=30)
    projects: list[ResumeEntry] = Field(default_factory=list, max_length=30)
    education: list[EducationEntry] = Field(default_factory=list, max_length=20)


class JDData(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str | None = Field(default=None, max_length=300)
    company: str | None = Field(default=None, max_length=300)
    location: str | None = Field(default=None, max_length=200)
    employment_type: str | None = Field(default=None, max_length=100)
    requirements: list[Annotated[str, Field(max_length=1000)]] = Field(default_factory=list, max_length=100)
    nice_to_have: list[Annotated[str, Field(max_length=1000)]] = Field(default_factory=list, max_length=100)
    responsibilities: list[Annotated[str, Field(max_length=1000)]] = Field(default_factory=list, max_length=100)
