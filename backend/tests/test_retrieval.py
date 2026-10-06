from unittest.mock import patch

from app.rag.retrieval import retrieve_chunks


def test_retrieve_chunks():

    fake_results = [
        {
            "content": "The proposed model uses attention.",
            "page": 4,
            "distance": 0.2,
            "similarity": 0.8
        },
        {
            "content": "The model is evaluated on three datasets.",
            "page": 5,
            "distance": 0.3,
            "similarity": 0.7
        }
    ]

    with patch(
        "app.rag.retrieval.generate_embeddings",
        return_value=[[0.1] * 768]
    ), patch(
        "app.rag.retrieval.psycopg.connect"
    ) as mock_connect:

        mock_cursor = mock_connect.return_value.cursor.return_value.__enter__.return_value

        mock_cursor.fetchall.return_value = [
            (
                "The proposed model uses attention.",
                4,
                0.2
            ),
            (
                "The model is evaluated on three datasets.",
                5,
                0.3
            )
        ]

        results = retrieve_chunks(
            query="What methodology is used?",
            paper_id="test-paper",
            top_k=2
        )

        assert len(results) == 2
        assert results[0]["page"] == 4
        assert results[0]["similarity"] == 0.8