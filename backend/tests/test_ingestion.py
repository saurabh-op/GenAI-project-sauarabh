from app.rag import ingestion


def test_extract_and_chunk_pdf_removes_null_characters(monkeypatch):
    class FakePage:
        def extract_text(self):
            return "Research\x00paper"

    class FakeReader:
        pages = [FakePage()]

    monkeypatch.setattr(ingestion, "PdfReader", lambda _: FakeReader())

    chunks = ingestion.extract_and_chunk_pdf("unused.pdf")

    assert chunks == [{"text": "Research paper", "page": 1}]
