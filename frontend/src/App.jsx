import { useRef, useState } from "react";
import "./App.css";

const reviewSections = [
  ["research_problem", "Research Problem"],
  ["literature_gap", "Literature Gap"],
  ["methodology", "Methodology"],
  ["experimental_design", "Experimental Design"],
  ["results_discussion", "Results & Discussion"],
  ["novelty_contribution", "Novelty & Contribution"],
  ["limitations", "Limitations"],
  ["overall_assessment", "Overall Assessment"],
];

const agents = [
  ["methodology_agent", "Methodology Agent"],
  ["novelty_agent", "Novelty Agent"],
  ["quality_agent", "Quality Agent"],
  ["final_reviewer", "Final Reviewer"],
];
const API_BASE_URL = (import.meta.env.VITE_API_URL || "http://127.0.0.1:8000").replace(/\/+$/, "");

function getErrorMessage(data, fallback) {
  return data?.detail || data?.error || fallback;
}

function ReviewCard({ title, data, isOverall }) {
  const renderList = (items) => (items?.length ? (
    <ul>{items.map((item, index) => <li key={`${title}-${index}`}>{item}</li>)}</ul>
  ) : <p className="empty-copy">No points provided.</p>);

  return (
    <article className={`review-card ${isOverall ? "review-card--overall" : ""}`}>
      <div className="card-heading">
        <div><span className="section-kicker">{isOverall ? "Final synthesis" : "Review section"}</span><h3>{title}</h3></div>
        <span className="card-mark">{isOverall ? "08" : "01"}</span>
      </div>
      <div className="assessment"><span className="content-label">Assessment</span><p>{data?.assessment || "No assessment provided."}</p></div>
      <div className="insight-grid">
        <div><span className="content-label content-label--positive">Strengths</span>{renderList(data?.strengths)}</div>
        <div><span className="content-label content-label--negative">Weaknesses</span>{renderList(data?.weaknesses)}</div>
      </div>
      <div className="evidence-list">
        <span className="content-label">Evidence</span>
        {data?.evidence?.length ? data.evidence.map((item, index) => (
          <div className="evidence" key={`${title}-evidence-${index}`}><span className="page-number">Page {item.page}</span><p>{item.text}</p></div>
        )) : <p className="empty-copy">No supporting evidence provided.</p>}
      </div>
    </article>
  );
}

function ReviewProgress({ progress }) {
  const completedAgents = progress?.completed_agents ?? 0;
  const totalAgents = progress?.total_agents ?? agents.length;
  const completionPercent = Math.round((completedAgents / totalAgents) * 100);

  return (
    <section className="progress-panel" role="status" aria-live="polite" aria-busy="true">
      <div className="progress-intro"><span className="loader-spinner loader-spinner--large" aria-hidden="true" /><div><span className="eyebrow">Processing paper</span><h2>AI review in progress</h2><p>The backend is retrieving evidence and running the review agents. This can take a little while; keep this page open.</p></div></div>
      <div className="progress-summary"><span>{completedAgents} of {totalAgents} agents complete</span><strong>{completionPercent}%</strong></div>
      <div className="progress-track" role="progressbar" aria-label="Review agent completion" aria-valuemin={0} aria-valuemax={totalAgents} aria-valuenow={completedAgents}>
        <span className={`progress-fill ${completedAgents < totalAgents ? "progress-fill--active" : ""}`} style={{ width: `${completionPercent}%` }} />
      </div>
      <div className="agent-list">{agents.map(([agentId, agentName]) => {
        const status = progress?.agents?.[agentId]?.status || "queued";
        const statusLabel = status === "completed" ? "Complete" : status === "running" ? "Working" : "Queued";
        return (
          <div className={`agent-step agent-step--${status}`} key={agentId}>
            <span className={`agent-status agent-status--${status}`} aria-hidden="true" />
            <span>{agentName}</span>
            <small>{statusLabel}</small>
          </div>
        );
      })}</div>
    </section>
  );
}

function App() {
  const [file, setFile] = useState(null);
  const [paperId, setPaperId] = useState("");
  const [message, setMessage] = useState(null);
  const [review, setReview] = useState(null);
  const [reviewProgress, setReviewProgress] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [reviewing, setReviewing] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const inputRef = useRef(null);

  const selectFile = (selectedFile) => {
    if (!selectedFile) return;
    if (selectedFile.type !== "application/pdf" && !selectedFile.name.toLowerCase().endsWith(".pdf")) {
      setMessage({ type: "error", text: "Please choose a PDF file to continue." });
      return;
    }
    setFile(selectedFile);
    setMessage(null);
    setPaperId("");
    setReview(null);
    setReviewProgress(null);
  };

  const uploadPaper = async () => {
    if (!file) {
      setMessage({ type: "error", text: "Select a PDF before uploading." });
      return;
    }
    const formData = new FormData();
    formData.append("file", file);
    setMessage({
      type: "loading",
      text: "Uploading and indexing paper...",
      detail: "The backend is extracting text, creating embeddings, and saving the paper. Keep this page open.",
    });
    setReview(null);
    setUploading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/upload`, { method: "POST", body: formData });
      const data = await response.json().catch(() => ({}));
      if (!response.ok || data.error || !data.paper_id) {
        throw new Error(getErrorMessage(data, "The backend did not return an indexed paper."));
      }
      setPaperId(data.paper_id);
      setMessage({ type: "success", text: "Paper uploaded successfully.", detail: `Paper indexed: ${data.chunks_created} chunks` });
    } catch (error) {
      setMessage({
        type: "error",
        text: error instanceof TypeError
          ? `Cannot reach the backend at ${API_BASE_URL}. Check that it is running and restart the frontend after changing .env.`
          : error.message || "Unable to process this PDF. Please check the file and try again.",
      });
    } finally {
      setUploading(false);
    }
  };

  const reviewPaper = async () => {
    if (!paperId) {
      setMessage({ type: "error", text: "Upload and index a paper before starting the review." });
      return;
    }
    setReviewing(true);
    setMessage({
      type: "loading",
      text: "AI agents are reviewing the paper...",
      detail: "The backend is retrieving evidence and generating the review.",
    });
    setReview(null);
    setReviewProgress(null);

    try {
      const response = await fetch(`${API_BASE_URL}/review/jobs`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ paper_id: paperId }),
      });
      let job = await response.json().catch(() => ({}));
      if (!response.ok || !job.job_id) {
        throw new Error(getErrorMessage(job, "Review request failed."));
      }
      setReviewProgress(job);

      while (job.status === "running") {
        await new Promise((resolve) => window.setTimeout(resolve, 1000));
        const statusResponse = await fetch(`${API_BASE_URL}/review/jobs/${encodeURIComponent(job.job_id)}`);
        const statusData = await statusResponse.json().catch(() => ({}));
        if (!statusResponse.ok) {
          throw new Error(getErrorMessage(statusData, "Could not retrieve review progress."));
        }
        job = statusData;
        setReviewProgress(job);
      }
      if (job.status !== "completed") {
        throw new Error(job.error || "The review did not complete successfully.");
      }

      let parsedReview = job.review;
      if (!parsedReview) throw new Error("The backend returned an empty review.");
      if (typeof parsedReview === "string") parsedReview = JSON.parse(parsedReview);
      setReview(parsedReview);
      setMessage({ type: "success", text: "Review completed successfully.", detail: "Evidence-backed findings are ready to explore." });
    } catch (error) {
      setMessage({ type: "error", text: error.message || "The AI review could not be completed. Please try again." });
    } finally {
      setReviewing(false);
    }
  };

  return (
    <main className="app">
      <section className="hero"><div className="hero-copy"><span className="eyebrow">AI research intelligence</span><h1>AI Research<br /><em>Paper Reviewer</em></h1><p>Upload a research paper and get an evidence-based review powered by RAG and multi-agent AI.</p><div className="tech-badge"><span className="status-dot" /> RAG <i /> LangGraph <i /> pgvector <i /> Gemini</div></div><div className="hero-visual" aria-hidden="true"><div className="visual-orbit orbit-one" /><div className="visual-orbit orbit-two" /><div className="visual-core">AI<span>+</span></div><span className="visual-label label-top">EVIDENCE</span><span className="visual-label label-bottom">RAG / 01</span></div></section>
      <section className="workspace-section"><div className="section-heading"><div><span className="eyebrow">01 / Ingest</span><h2>Start with your paper</h2></div><span className="step-count">01 <span>/ 02</span></span></div><div className="upload-card"><div className={`dropzone ${dragActive ? "dropzone--active" : ""} ${file ? "dropzone--selected" : ""}`} onDragOver={(event) => { event.preventDefault(); setDragActive(true); }} onDragLeave={() => setDragActive(false)} onDrop={(event) => { event.preventDefault(); setDragActive(false); selectFile(event.dataTransfer.files[0]); }} onClick={() => inputRef.current?.click()} onKeyDown={(event) => { if (event.key === "Enter" || event.key === " ") inputRef.current?.click(); }} role="button" tabIndex="0" aria-label="Choose a research paper PDF"><input ref={inputRef} type="file" accept="application/pdf,.pdf" onChange={(event) => selectFile(event.target.files[0])} /><div className="pdf-icon">PDF</div><div className="dropzone-copy"><strong>{file ? file.name : "Upload Research Paper"}</strong><span>{file ? "Ready to be indexed" : "Drag & drop your PDF here or browse"}</span><small>PDF files only - up to 25 MB</small></div><span className="browse-link">Browse <span aria-hidden="true">↗</span></span></div><div className="upload-footer"><div className="file-meta">{file ? <><span className="file-check">OK</span><span>{file.name}</span></> : <><span className="file-check file-check--muted">+</span><span>No paper selected</span></>}</div><div className="upload-actions"><button className="button button--primary" onClick={uploadPaper} disabled={uploading || !file}>{uploading ? <><span className="loader-spinner" aria-hidden="true" /> Indexing...</> : "Upload & index"}<span aria-hidden="true">-&gt;</span></button>{paperId && !review && <button className="button button--dark" onClick={reviewPaper} disabled={reviewing}>Review Paper <span aria-hidden="true">-&gt;</span></button>}</div></div>{message && <div className={`message message--${message.type}`} role={message.type === "error" ? "alert" : "status"} aria-busy={message.type === "loading"}><span className={`message-icon ${message.type === "loading" ? "message-icon--loading" : ""}`} aria-hidden="true">{message.type === "loading" ? <span className="loader-spinner" /> : message.type === "error" ? "!" : "OK"}</span><span><strong>{message.text}</strong>{message.detail && <small>{message.detail}</small>}</span></div>}</div></section>
      {paperId && !review && !reviewing && <section className="review-cta"><div><span className="eyebrow">02 / Review</span><h2>Your paper is ready</h2><p>Run the agent workflow to turn indexed passages into a structured academic assessment.</p></div><button className="button button--dark" onClick={reviewPaper}>Review Paper <span aria-hidden="true">-&gt;</span></button></section>}
      {reviewing && <ReviewProgress progress={reviewProgress} />}
      {!review && !reviewing && !paperId && <section className="empty-state"><div className="empty-icon">+</div><span className="eyebrow">Your review space</span><h2>Start your paper review</h2><p>Upload a research paper to generate an evidence-based assessment of its methodology, novelty, experiments and overall quality.</p></section>}
      {review && <section className="review-section"><div className="review-header"><div><span className="eyebrow">Completed review</span><h2>Research Paper Review</h2><p>Structured findings grounded in the paper's retrieved evidence.</p></div><div className="review-header-actions"><span className="review-status"><span className="status-dot" /> Analysis complete</span><button className="button button--dark" type="button" onClick={reviewPaper} disabled={reviewing}>Review again <span aria-hidden="true">↻</span></button></div></div><div className="review-grid">{reviewSections.map(([key, title], index) => <ReviewCard key={key} title={title} data={review[key] || {}} isOverall={index === reviewSections.length - 1} />)}</div></section>}
      <footer className="footer"><span>Academic Review Workspace</span><span>Built for rigorous reading</span></footer>
    </main>
  );
}

export default App;