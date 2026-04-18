from pydantic import BaseModel
from typing import List, Optional

class SkillCategories(BaseModel):
    languages: List[str] = []
    frameworks: List[str] = []
    tools: List[str] = []
    cloud: List[str] = []
    databases: List[str] = []
    concepts: List[str] = []

class MatchBreakdown(BaseModel):
    languages: float = 0.0
    frameworks: float = 0.0
    tools: float = 0.0
    cloud: float = 0.0
    databases: float = 0.0
    concepts: float = 0.0

class AnalysisResult(BaseModel):
    decision: str
    confidence: int
    matched_skills: List[str]
    missing_skills: List[str]
    resume_skills: List[str]
    job_skills: List[str]
    resume_skill_categories: SkillCategories
    job_skill_categories: SkillCategories
    match_breakdown: MatchBreakdown
    suggestions: List[str]
    resume_filename: str
    job_description_source: str
    s3_resume_key: Optional[str] = None
    s3_jd_key: Optional[str] = None

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None