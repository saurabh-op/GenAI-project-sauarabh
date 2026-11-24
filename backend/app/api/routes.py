import copy
import logging
import os
import threading
import uuid

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel

from fastapi import UploadFile, File

from app.rag.ingestion import extract_and_chunk_pdf
from app.services.embedding_service import generate_embeddings
from app.rag.vector_store import store_chunks

from app.agents.review_graph import review_graph

router=APIRouter()
logger = logging.getLogger(__name__)

_REVIEW_JOBS = {}
_REVIEW_JOBS_LOCK = threading.Lock()
_SPECIALIST_NODES = {
    "methodology_agent": ("methodology_agent", "methodology_review"),
    "novelty_agent": ("novelty_agent", "novelty_review"),
    "quality_agent": ("quality_agent", "quality_review"),
}
_TOTAL_REVIEW_AGENTS = len(_SPECIALIST_NODES) + 1

class ReviewRequest(BaseModel):
    paper_id: str


def _public_review_job(job):
    return {
        key: copy.deepcopy(job[key])
        for key in (
            "job_id",
            "status",
            "agents",
            "completed_agents",
            "total_agents",
            "review",
            "error",
        )
    }


def _run_review_job(job_id, paper_id):
    try:
        for update in review_graph.stream(
            {"paper_id": paper_id},
            stream_mode="updates",
        ):
            with _REVIEW_JOBS_LOCK:
                job = _REVIEW_JOBS[job_id]

                if "supervisor" in update:
                    for agent_id, _ in _SPECIALIST_NODES.values():
                        job["agents"][agent_id]["status"] = "running"

                for node_name, (agent_id, result_key) in _SPECIALIST_NODES.items():
                    if node_name in update:
                        node_result = update[node_name]
                        job["agent_results"][agent_id] = node_result.get(result_key)
                        job["agents"][agent_id]["status"] = "completed"

                if all(
                    job["agents"][agent_id]["status"] == "completed"
                    for agent_id, _ in _SPECIALIST_NODES.values()
                ):
                    job["agents"]["final_reviewer"]["status"] = "running"

                if "final_reviewer" in update:
                    job["review"] = update["final_reviewer"].get("final_review")
                    job["agents"]["final_reviewer"]["status"] = "completed"

                job["completed_agents"] = sum(
                    agent["status"] == "completed"
                    for agent in job["agents"].values()
                )

        with _REVIEW_JOBS_LOCK:
            job = _REVIEW_JOBS[job_id]
            if not job["review"]:
                raise RuntimeError("Review graph finished without a final review.")
            job["status"] = "completed"
    except Exception:
        logger.exception("Review job %s failed", job_id)
        with _REVIEW_JOBS_LOCK:
            job = _REVIEW_JOBS.get(job_id)
            if job is not None:
                job["status"] = "failed"
                job["error"] = "Review processing failed. Check the backend logs."


@router.post("/review/jobs")
def start_review_job(request: ReviewRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    with _REVIEW_JOBS_LOCK:
        _REVIEW_JOBS[job_id] = {
            "job_id": job_id,
            "status": "running",
            "agents": {
                "methodology_agent": {"status": "queued"},
                "novelty_agent": {"status": "queued"},
                "quality_agent": {"status": "queued"},
                "final_reviewer": {"status": "queued"},
            },
            "completed_agents": 0,
            "total_agents": _TOTAL_REVIEW_AGENTS,
            "agent_results": {},
            "review": None,
            "error": None,
        }

    background_tasks.add_task(_run_review_job, job_id, request.paper_id)
    with _REVIEW_JOBS_LOCK:
        return _public_review_job(_REVIEW_JOBS[job_id])


@router.get("/review/jobs/{job_id}")
def get_review_job(job_id: str):
    with _REVIEW_JOBS_LOCK:
        job = _REVIEW_JOBS.get(job_id)
        if job is None:
            raise HTTPException(status_code=404, detail="Review job not found.")
        return _public_review_job(job)
    
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
        raise HTTPException(
            status_code=422,
            detail="Could not extract readable text from this PDF. Upload a text-based PDF.",
        )

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

  

