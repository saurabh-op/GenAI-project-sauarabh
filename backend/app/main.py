from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(title="AI Research Paper Reviewer")

app.include_router(router)

@app.get("/")
def health_check():
    return {"status": "running"}


@app.get("/health")
def health():
    return {"status": "healthy"}
