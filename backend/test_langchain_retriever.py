from app.rag.langchain_retriever import ResearchPaperRetriever
retriever = ResearchPaperRetriever(
    paper_id="04980ce8-e196-4050-b36f-abe619710578",
    top_k=1
)

documents = retriever.invoke(
    "What methodology does this paper use?"
)
print("Documents retrieved:", len(documents))

for i, document in enumerate(documents, start=1):
    print(f"\n--- Document {i} ---")
    print("Page:", document.metadata["page"])
    print(document.page_content[:300])