from pydantic import BaseModel
from typing import List, Optional
from app.models.skill import ExtractedSkill

class ExtractedExperience(BaseModel):
    company: str
    role: str
    duration_months: int
    description: str
    skills_used: List[str]

class ParsedResume(BaseModel):
    full_name: str
    email: Optional[str]
    phone: Optional[str]
    current_role: str
    years_total_experience: int
    skills: List[ExtractedSkill]
    experience: List[ExtractedExperience]
    education: List[str]
    certifications: List[str]
    industry: str
    summary: str
