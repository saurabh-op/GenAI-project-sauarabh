from fastapi.testclient import TestClient

from app.api import routes
from app.main import app


client = TestClient(app)


def test_upload_returns_paper_id_when_indexing_succeeds(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        routes,
        "extract_and_chunk_pdf",
        lambda _: [{"text": "Paper content", "page": 1}],
    )
    monkeypatch.setattr(routes, "generate_embeddings", lambda _: [[0.1] * 768])
    monkeypatch.setattr(routes, "store_chunks", lambda **_: None)

    response = client.post(
        "/upload",
        files={"file": ("paper.pdf", b"%PDF-1.4 test", "application/pdf")},
    )

    assert response.status_code == 200
    assert response.json()["paper_id"]
    assert response.json()["chunks_created"] == 1


def test_upload_returns_error_when_pdf_has_no_readable_text(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(routes, "extract_and_chunk_pdf", lambda _: [])

    response = client.post(
        "/upload",
        files={"file": ("paper.pdf", b"%PDF-1.4 test", "application/pdf")},
    )

    assert response.status_code == 422
    assert "readable text" in response.json()["detail"]


def test_review_job_tracks_agent_completion(monkeypatch):
    class FakeReviewGraph:
        def stream(self, state, stream_mode):
            assert state == {"paper_id": "paper-123"}
            assert stream_mode == "updates"
            yield {"supervisor": {}}
            yield {"methodology_agent": {"methodology_review": {"assessment": "Methodology"}}}
            yield {"novelty_agent": {"novelty_review": {"assessment": "Novelty"}}}
            yield {"quality_agent": {"quality_review": {"assessment": "Quality"}}}
            yield {"final_reviewer": {"final_review": {"overall_assessment": "Complete"}}}

    monkeypatch.setattr(routes, "review_graph", FakeReviewGraph())

    start_response = client.post("/review/jobs", json={"paper_id": "paper-123"})

    assert start_response.status_code == 200
    job_id = start_response.json()["job_id"]

    status_response = client.get(f"/review/jobs/{job_id}")
    status = status_response.json()

    assert status_response.status_code == 200
    assert status["status"] == "completed"
    assert status["completed_agents"] == 4
    assert status["agents"]["methodology_agent"]["status"] == "completed"
    assert status["agents"]["final_reviewer"]["status"] == "completed"
    assert status["review"]["overall_assessment"] == "Complete"