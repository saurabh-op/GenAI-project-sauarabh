from app.rag.retrieval import retrieve_chunks
from app.services.llm_service import generate_review

query = "What methodology does this paper use, and what are its weaknesses?"

chunks = retrieve_chunks(
    query=query,
    paper_id="sample-paper",
    top_k=5
)

answer = generate_review(
    query=query,
    retrieved_chunks=chunks
)

print("\n===== RAG REVIEW =====\n")
print(answer)
