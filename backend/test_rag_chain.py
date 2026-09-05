from app.rag.rag_chain import create_rag_chain


paper_id = "04980ce8-e196-4050-b36f-abe619710578"

rag_chain = create_rag_chain(paper_id)

result = rag_chain(
    "What methodology does this paper use?"
)

print("\n===== ANSWER =====")
print(result["answer"])

print("\n===== SOURCES =====")

for source in result["sources"]:
    print(f"\nPage {source['page']}")
    print(source["content"][:300])