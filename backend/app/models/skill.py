from pydantic import BaseModel, Field

class ExtractedSkill(BaseModel):
    name: str = Field(description="Skill name")
    category: str = Field(description="Category: technical, soft, domain")
    proficiency: int = Field(description="Estimated proficiency 1-5")
    years_experience: float = Field(description="Years of experience with skill")
