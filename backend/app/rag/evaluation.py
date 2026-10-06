def evaluate_retrieval(results, similarity_threshold=0.5):
    if not results:
        return {
            "retrieved_chunks": 0,
            "relevant_chunks": 0,
            "retrieval_quality": "poor"
        }

    relevant_chunks = [
        result
        for result in results
        if result["similarity"] >= similarity_threshold
    ]

    relevant_count = len(relevant_chunks)

    if relevant_count >= 3:
        quality = "good"
    elif relevant_count >= 1:
        quality = "moderate"
    else:
        quality = "poor"

    return {
        "retrieved_chunks": len(results),
        "relevant_chunks": relevant_count,
        "retrieval_quality": quality
    }