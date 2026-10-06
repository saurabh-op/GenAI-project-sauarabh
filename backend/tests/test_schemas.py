from app.agents.schemas import AgentReview, Evidence, FinalReview


def test_agent_review_schema():

    review = AgentReview(
        assessment="The methodology is clearly described.",
        strengths=["Clear architecture"],
        weaknesses=["Small dataset"],
        evidence=[
            Evidence(
                page=4,
                text="The proposed model uses..."
            )
        ]
    )

    assert review.assessment
    assert len(review.evidence) == 1


def test_final_review_schema():

    section = AgentReview(
        assessment="Good",
        strengths=[],
        weaknesses=[],
        evidence=[]
    )

    review = FinalReview(
        research_problem=section,
        literature_gap=section,
        methodology=section,
        experimental_design=section,
        results_discussion=section,
        novelty_contribution=section,
        limitations=section,
        overall_assessment=section
    )

    assert review.methodology.assessment == "Good"
    assert review.overall_assessment.assessment == "Good"
    