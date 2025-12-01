from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class Exercise(BaseModel):
    subject: str
    concept: str
    level: str
    prompt: str
    answer: str
    meta: Dict = Field(default_factory=dict)

class GradeResult(BaseModel):
    score: int
    max_score: int
    feedback: str
    next_step: Optional[str] = None

class QAResult(BaseModel):
    explanation: str
    concepts: List[str]
    estimated_level: str