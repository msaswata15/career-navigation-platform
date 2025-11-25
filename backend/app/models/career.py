from pydantic import BaseModel
from typing import List, Optional, Dict

class CareerPathRequest(BaseModel):
    current_role: str
    target_role: Optional[str] = None
    user_skills: List[str]

class CareerPathResponse(BaseModel):
    paths: List[Dict]
    recommended_path: Optional[Dict] = None
    skill_gaps: List[Dict]
