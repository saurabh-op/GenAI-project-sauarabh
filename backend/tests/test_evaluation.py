from app.rag.evaluation import evaluate_retrieval


def test_good_retrieval():

    results = [
        {"similarity": 0.8},
        {"similarity": 0.7},
        {"similarity": 0.9}
    ]

    result = evaluate_retrieval(results)

    assert result["retrieved_chunks"] == 3
    assert result["relevant_chunks"] == 3
    assert result["retrieval_quality"] == "good"


def test_empty_retrieval():

    result = evaluate_retrieval([])

    assert result["retrieved_chunks"] == 0
    assert result["relevant_chunks"] == 0
    assert result["retrieval_quality"] == "poor"