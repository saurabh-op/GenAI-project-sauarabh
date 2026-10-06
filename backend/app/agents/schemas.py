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

class FinalReview(BaseModel):
    research_problem: AgentReview
    literature_gap: AgentReview
    methodology: AgentReview
    experimental_design: AgentReview
    results_discussion: AgentReview
    novelty_contribution: AgentReview
    limitations: AgentReview
    overall_assessment: AgentReview