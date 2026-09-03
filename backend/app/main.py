from fastapi import FastAPI

app = FastAPI(title="AI Code Review Assistant")


@app.get("/")
def health_check():
    return {"status": "running"}


@app.get("/health")
def health():
    return {"status": "healthy"}
