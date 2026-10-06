# AI Research Paper Reviewer

Upload a research paper in PDF format and get a structured, evidence-based review. The application extracts and indexes the paper, then uses retrieval-augmented generation (RAG) and specialist AI agents to assess its methodology, novelty, experiments, and overall quality.

## Features

- Upload a PDF and extract page-aware text chunks.
- Generate Gemini embeddings and store them in PostgreSQL with pgvector.
- Retrieve paper passages relevant to each review topic.
- Run a LangGraph workflow with methodology, novelty, and research-quality reviewers, followed by a final synthesis.
- View structured assessments, strengths, weaknesses, and page-referenced evidence in the web interface.

## Architecture

```mermaid
flowchart LR
    User --> UI["React + Vite frontend"]
    UI -->|"POST /upload and /review"| API["FastAPI backend"]
    API --> PDF["PDF extraction and chunking"]
    PDF --> Embed["Gemini embeddings"]
    Embed --> DB[("PostgreSQL + pgvector")]
    API --> Graph["LangGraph review workflow"]
    Graph --> Retrieve["Retrieve relevant paper chunks"]
    Retrieve --> DB
    Graph --> Gemini["Gemini review agents"]
    Gemini --> Graph
    Graph --> API
    API --> UI
```

### Review flow

1. The frontend sends a PDF to the backend.
2. The backend extracts text page by page, splits it into chunks, creates embeddings with Gemini, and stores each chunk and its page number in `paper_chunks`.
3. The frontend requests a review using the returned `paper_id`.
4. Three specialist agents retrieve relevant chunks and review methodology, novelty, and research quality. A final reviewer combines their assessments into a structured response.
5. The frontend displays the assessments, strengths, weaknesses, and evidence pages.

The backend keeps uploaded PDFs under `app/rag/documents` and stores their searchable chunks and embeddings in PostgreSQL. Text extraction uses pypdf; scanned PDFs without an extractable text layer need OCR before they can be reviewed.

## Technology

| Area | Technologies |
| --- | --- |
| Frontend | React, Vite |
| Backend API | Python 3.12, FastAPI, Uvicorn |
| Review workflow | LangGraph, LangChain |
| LLM and embeddings | Google Gemini |
| Vector storage | PostgreSQL, pgvector |
| PDF processing | pypdf |

## Prerequisites

- Python 3.12
- Node.js and npm
- A PostgreSQL database with the [pgvector](https://github.com/pgvector/pgvector) extension
- A Google Gemini API key

## Configuration

### Backend

Create `backend/.env`:

```dotenv
GEMINI_API_KEY=your_gemini_api_key
DATABASE_URL=postgresql://username:password@host:5432/database_name
```

Use your database provider's connection string. If the provider requires TLS, include the appropriate SSL parameters in `DATABASE_URL`.

Create the extension and table in that database before uploading a paper:

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS paper_chunks (
    id BIGSERIAL PRIMARY KEY,
    paper_id TEXT NOT NULL,
    content TEXT NOT NULL,
    page_number INTEGER NOT NULL,
    metadata TEXT NOT NULL DEFAULT '{}',
    embedding VECTOR(768) NOT NULL
);

CREATE INDEX IF NOT EXISTS paper_chunks_embedding_idx
    ON paper_chunks USING hnsw (embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS paper_chunks_paper_id_idx
    ON paper_chunks (paper_id);
```

The embedding column dimension must remain `768`, matching the Gemini embedding configuration in the backend. The HNSW index is optional for correctness, but can improve vector search performance.

### Frontend

Create `frontend/.env.local`:

```dotenv
VITE_API_URL=http://127.0.0.1:8000
```

Vite reads this value when it starts. Restart the frontend dev server after changing it. `VITE_` variables are included in the browser bundle; do not put API secrets in frontend environment files.

## Run locally

Open two terminals from the project directory.

### 1. Start the backend

In PowerShell:

```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

The API listens at `http://127.0.0.1:8000`. Check `http://127.0.0.1:8000/health` for its health response and open `http://127.0.0.1:8000/docs` for interactive API documentation.

### 2. Start the frontend

In the second terminal:

```powershell
cd frontend
npm ci
npm run dev
```

Open the local URL printed by Vite (usually `http://localhost:5173`). The backend CORS configuration permits `localhost:5173` and `127.0.0.1:5173`.

## API

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/` | Basic running status |
| `GET` | `/health` | Health check |
| `POST` | `/upload` | Accepts multipart form data with a `file` PDF; returns a `paper_id` and chunk count |
| `POST` | `/review` | Accepts JSON with a `paper_id`; returns the structured review |

Example review request:

```json
{
  "paper_id": "paper-id-returned-by-upload"
}
```

For the complete request and response schemas, use the FastAPI docs at `/docs` while the backend is running.

## Project layout

```text
backend/
  app/
    agents/       LangGraph state, schemas, and review workflow
    api/          FastAPI routes
    rag/          PDF ingestion, retrieval, and vector storage
    services/     Gemini LLM and embedding integrations
  requirements.txt
  DockerFile
frontend/
  src/            React application and styles
  package.json
```

## Development checks

Run the frontend lint and production build from `frontend/`:

```powershell
npm run lint
npm run build
```

The backend also contains exploratory test scripts. They may require working Gemini credentials, database connectivity, or previously indexed paper data; configure those dependencies before running them.

## Docker

The backend image can be built from the backend directory:

```powershell
cd backend
docker build -f DockerFile -t ai-research-paper-reviewer-api .
docker run --rm -p 8000:8000 --env-file .env ai-research-paper-reviewer-api
```

The container still requires a reachable PostgreSQL/pgvector database. When using Docker Desktop, `localhost` inside the container refers to the container itself; use a database hostname reachable from the container. Uploaded PDF files are kept inside the container by default; mount persistent storage at `/app/app/rag/documents` if those source PDFs need to survive container replacement.
