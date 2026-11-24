from types import SimpleNamespace

import pytest

from app.agents import review_graph


@pytest.mark.parametrize(
    "agent",
    [
        review_graph.methodology_agent,
        review_graph.novelty_agent,
        review_graph.quality_agent,
    ],
)
def test_review_agents_prompt_with_retrieved_context(agent, monkeypatch):
    prompts = []
    retrieval_limits = []

    class FakeRetriever:
        def __init__(self, paper_id, top_k):
            assert paper_id == "paper-123"
            retrieval_limits.append(top_k)

        def invoke(self, _query):
            return [
                SimpleNamespace(
                    metadata={"page": 7},
                    page_content="distinctive retrieved paper evidence",
                )
            ]

    class FakeChatModel:
        def with_structured_output(self, _schema):
            return self

        def invoke(self, prompt):
            prompts.append(prompt)
            return SimpleNamespace(model_dump=lambda: {})

    monkeypatch.setattr(review_graph, "ResearchPaperRetriever", FakeRetriever)
    monkeypatch.setattr(
        review_graph,
        "ChatGoogleGenerativeAI",
        lambda **_kwargs: FakeChatModel(),
    )

    agent({"paper_id": "paper-123"})

    assert retrieval_limits == [3]
    assert "distinctive retrieved paper evidence" in prompts[0]
    assert "[Page7]" in prompts[0]
