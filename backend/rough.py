from app.rag.ingestion import extract_and_chunk_pdf

chunks = extract_and_chunk_pdf(
    "app/rag/documents/sample.pdf"
)

print("Number of chunks:", len(chunks))

for chunk in chunks[:3]:
    print("\nPage:", chunk["page"])
    print(chunk["text"][:300])