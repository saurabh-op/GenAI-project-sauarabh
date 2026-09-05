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
    paper_id:str
    query:str

@router.post("/review")
def review_paper(request: ReviewRequest):
    

    # result =review_graph.invoke({
    #     "paper_id":request.paper_id
    # })
        

    # return {
    #     "paper_id": request.paper_id,
    #     "review": result["final_review"]
    # }
    return {
            "final_review": {
                "research_problem": {
                    "assessment": "The research problem is clearly defined.",
                    "strengths": [
                        "The problem is relevant.",
                        "The motivation is clearly explained."
                    ],
                    "weaknesses": [
                        "The problem scope could be more precise."
                    ],
                    "evidence": [
                        {
                            "page": 1,
                            "text": "The paper clearly states the research objective."
                        }
                    ]
                },
    
                "literature_gap": {
                    "assessment": "The paper identifies a reasonable gap in existing research.",
                    "strengths": [
                        "Relevant prior work is discussed."
                    ],
                    "weaknesses": [
                        "The gap could be supported with more recent studies."
                    ],
                    "evidence": []
                },
    
                "methodology": {
                    "assessment": "The proposed methodology is technically reasonable.",
                    "strengths": [
                        "The methodology is structured."
                    ],
                    "weaknesses": [
                        "Some implementation details are insufficiently explained."
                    ],
                    "evidence": []
                },
    
                "experimental_design": {
                    "assessment": "The experimental setup provides a reasonable basis for evaluation.",
                    "strengths": [],
                    "weaknesses": [],
                    "evidence": []
                },
    
                "results_discussion": {
                    "assessment": "The results indicate that the proposed approach performs reasonably well.",
                    "strengths": [],
                    "weaknesses": [],
                    "evidence": []
                },
    
                "novelty_contribution": {
                    "assessment": "The work provides a meaningful contribution.",
                    "strengths": [],
                    "weaknesses": [],
                    "evidence": []
                },
    
                "limitations": {
                    "assessment": "The paper has several limitations that should be discussed more explicitly.",
                    "strengths": [],
                    "weaknesses": [],
                    "evidence": []
                },
    
                "overall_assessment": {
                    "assessment": "Overall, the paper presents a promising research contribution.",
                    "strengths": [
                        "Clear research motivation.",
                        "Reasonable methodology."
                    ],
                    "weaknesses": [
                        "More extensive evaluation would strengthen the work."
                    ],
                    "evidence": []
                }
            }
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

