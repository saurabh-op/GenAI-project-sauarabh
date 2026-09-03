from fastapi import APIRouter
from pydantic import BaseModel
import os
import uuid

from fastapi import UploadFile, File
from app.rag.retrieval import retrieve_chunks
from app.services.llm_service import generate_review

from app.rag.ingestion import extract_and_chunk_pdf
from app.services.embedding_service import generate_embeddings
from app.rag.vector_store import store_chunks

router=APIRouter()

class ReviewRequest(BaseModel):
    paper_id:str
    query:str

@router.post("/review")
def review_paper(request: ReviewRequest):

    queries = [
        "research problem and clarity",
        "literature review and research gap",
        "methodology and proposed approach",
        "experimental design and evaluation",
        "results and discussion",
        "novelty and contribution",
        "limitations",
        "strengths and weaknesses"
    ]

    all_chunks = []

    for query in queries:
        chunks = retrieve_chunks(
            query=query,
            paper_id=request.paper_id,
            top_k=3
        )

        all_chunks.extend(chunks)

    review = generate_review(
        retrieved_chunks=all_chunks
    )

    return {
        "paper_id": request.paper_id,
        "review": review
    }



@router.post("/upload")
async def upload_paper(file:UploadFile=File(...)):
    paper_id=str(uuid.uuid4())
    upload_dir="app/rag/documents"
    os.makedirs(upload_dir,exist_ok=True)
    file_path=f"{upload_dir}/{paper_id}.pdf"
    with open(file_path,"wb") as buffer:
        buffer.write(await file.read())

    chunks=extract_and_chunk_pdf(file_path)

    if not chunks:
        return {
            "error":"Could not extract text from the pdf"

        }

    texts=[chunk["text"] for chunk in chunks]
    embeddings=generate_embeddings(texts)

    store_chunks(
        paper_id=paper_id,
        chunks=chunks,
        embeddings=embeddings
    )

    return {
        "paper_id":paper_id,
        "filename": file.filename,
        "chunks_created":len(chunks),
        "message":"Paper Uploaded successfully"
    }