from pydantic import BaseModel
from typing import List


class Evidence(BaseModel):
    page: int
    text: str


class AgentReview(BaseModel):
    assessment: str
    strengths: List[str]
    weaknesses: List[str]
    evidence: List[Evidence]