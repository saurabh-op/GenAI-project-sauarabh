from fastapi import APIRouter
from pydantic import BaseModel
import os
import uuid

from fastapi import UploadFile, File

from app.rag.ingestion import extract_and_chunk_pdf
from app.services.embedding_service import generate_embeddings
from app.rag.vector_store import store_chunks

from app.agents.review_graph import review_graph

router=APIRouter()

class ReviewRequest(BaseModel):
    paper_id: str
    
@router.post("/review")
def review_paper(request: ReviewRequest):
    

    result =review_graph.invoke({
        "paper_id":request.paper_id
    })
        

    return {
        "paper_id": request.paper_id,
        "review": result["final_review"]
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

  

