from app.rag.retrieval import retrieve_chunks

results=retrieve_chunks(
    query="What methodology does this paper use?",
    paper_id="sample-paper",
    top_k=5
)

for i, result in enumerate(results, start=1):
    print(f"\n--- Result {i} ---")
    print("Page:", result["page"])
    print("Distance:", result["distance"])
    print(result["content"][:500])