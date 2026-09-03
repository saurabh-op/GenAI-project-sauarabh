from app.rag.ingestion import extract_and_chunk_pdf
from app.services.embedding_service import generate_embeddings
from app.rag.vector_store import store_chunks

PDF_PATH = "app/rag/documents/sample.pdf"

chunks = extract_and_chunk_pdf(PDF_PATH)

print("Chunks created:", len(chunks))

texts = [chunk["text"] for chunk in chunks]

embeddings = generate_embeddings(texts)
print("Embeddings generated:", len(embeddings))
print("Embedding dimension:", len(embeddings[0]))

store_chunks(
    paper_id="sample-paper",
    chunks=chunks,
    embeddings=embeddings
)

print("Chunks stored successfully in pgvector!")