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

const agents = ["Methodology Agent", "Novelty Agent", "Quality Agent", "Final Reviewer"];

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

function ReviewProgress() {
  return (
    <section className="progress-panel" aria-live="polite">
      <div className="progress-intro"><span className="pulse-ring" aria-hidden="true" /><div><span className="eyebrow">Processing paper</span><h2>AI review in progress</h2><p>Four specialist agents are reading the paper and grounding their findings in retrieved passages.</p></div></div>
      <div className="agent-list">{agents.map((agent, index) => <div className={`agent-step ${index === 0 ? "agent-step--active" : ""}`} key={agent}><span className="agent-status" aria-hidden="true" /><span>{agent}</span><small>{index === 0 ? "Analyzing" : "Queued"}</small></div>)}</div>
    </section>
  );
}

function App() {
  const [file, setFile] = useState(null);
  const [paperId, setPaperId] = useState("");
  const [message, setMessage] = useState(null);
  const [review, setReview] = useState(null);
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
  };

  const uploadPaper = async () => {
    if (!file) {
      setMessage({ type: "error", text: "Select a PDF before uploading." });
      return;
    }
    const formData = new FormData();
    formData.append("file", file);
    setMessage({ type: "loading", text: "Uploading and indexing paper..." });
    setReview(null);
    setUploading(true);

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/upload`, { method: "POST", body: formData });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        setMessage({ type: "error", text: "Unable to process this PDF. Please check the file and try again." });
        return;
      }
      setPaperId(data.paper_id);
      setMessage({ type: "success", text: "Paper uploaded successfully.", detail: `Paper indexed: ${data.chunks_created} chunks` });
    } catch {
      setMessage({ type: "error", text: "Unable to process this PDF. Please check the file and try again." });
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
    setMessage({ type: "loading", text: "AI agents are reviewing the paper..." });
    setReview(null);

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/review`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ paper_id: paperId, query: "Review this research paper" }),
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error("Review request failed.");
      let parsedReview = data.review ?? data.final_review;
      if (!parsedReview) throw new Error("The backend returned an empty review.");
      if (typeof parsedReview === "string") parsedReview = JSON.parse(parsedReview);
      setReview(parsedReview);
      setMessage({ type: "success", text: "Review completed successfully.", detail: "Evidence-backed findings are ready to explore." });
    } catch {
      setMessage({ type: "error", text: "The AI review could not be completed. Please try again." });
    } finally {
      setReviewing(false);
    }
  };

  return (
    <main className="app">
      <header className="site-header"><div className="brand"><span className="brand-mark">AR</span><span>Academic Review</span></div><span className="header-note">Evidence-led analysis workspace</span></header>
      <section className="hero"><div className="hero-copy"><span className="eyebrow">AI research intelligence</span><h1>AI Research<br /><em>Paper Reviewer</em></h1><p>Upload a research paper and get an evidence-based review powered by RAG and multi-agent AI.</p><div className="tech-badge"><span className="status-dot" /> RAG <i /> LangGraph <i /> pgvector <i /> Gemini</div></div><div className="hero-visual" aria-hidden="true"><div className="visual-orbit orbit-one" /><div className="visual-orbit orbit-two" /><div className="visual-core">AI<span>+</span></div><span className="visual-label label-top">EVIDENCE</span><span className="visual-label label-bottom">RAG / 01</span></div></section>
      <section className="workspace-section"><div className="section-heading"><div><span className="eyebrow">01 / Ingest</span><h2>Start with your paper</h2></div><span className="step-count">01 <span>/ 02</span></span></div><div className="upload-card"><div className={`dropzone ${dragActive ? "dropzone--active" : ""} ${file ? "dropzone--selected" : ""}`} onDragOver={(event) => { event.preventDefault(); setDragActive(true); }} onDragLeave={() => setDragActive(false)} onDrop={(event) => { event.preventDefault(); setDragActive(false); selectFile(event.dataTransfer.files[0]); }} onClick={() => inputRef.current?.click()} onKeyDown={(event) => { if (event.key === "Enter" || event.key === " ") inputRef.current?.click(); }} role="button" tabIndex="0" aria-label="Choose a research paper PDF"><input ref={inputRef} type="file" accept="application/pdf,.pdf" onChange={(event) => selectFile(event.target.files[0])} /><div className="pdf-icon">PDF</div><div className="dropzone-copy"><strong>{file ? file.name : "Upload Research Paper"}</strong><span>{file ? "Ready to be indexed" : "Drag & drop your PDF here or browse"}</span><small>PDF files only - up to 25 MB</small></div><span className="browse-link">Browse <span aria-hidden="true">↗</span></span></div><div className="upload-footer"><div className="file-meta">{file ? <><span className="file-check">OK</span><span>{file.name}</span></> : <><span className="file-check file-check--muted">+</span><span>No paper selected</span></>}</div><div className="upload-actions"><button className="button button--primary" onClick={uploadPaper} disabled={uploading || !file}>{uploading ? "Indexing..." : "Upload & index"}<span aria-hidden="true">-&gt;</span></button>{paperId && !review && <button className="button button--dark" onClick={reviewPaper} disabled={reviewing}>Review Paper <span aria-hidden="true">-&gt;</span></button>}</div></div>{message && <div className={`message message--${message.type}`} role={message.type === "error" ? "alert" : "status"}><span className="message-icon">{message.type === "error" ? "!" : message.type === "success" ? "OK" : "..."}</span><span><strong>{message.text}</strong>{message.detail && <small>{message.detail}</small>}</span></div>}</div></section>
      {paperId && !review && !reviewing && <section className="review-cta"><div><span className="eyebrow">02 / Review</span><h2>Your paper is ready</h2><p>Run the agent workflow to turn indexed passages into a structured academic assessment.</p></div><button className="button button--dark" onClick={reviewPaper}>Review Paper <span aria-hidden="true">-&gt;</span></button></section>}
      {reviewing && <ReviewProgress />}
      {!review && !reviewing && !paperId && <section className="empty-state"><div className="empty-icon">+</div><span className="eyebrow">Your review space</span><h2>Start your paper review</h2><p>Upload a research paper to generate an evidence-based assessment of its methodology, novelty, experiments and overall quality.</p></section>}
      {review && <section className="review-section"><div className="review-header"><div><span className="eyebrow">Completed review</span><h2>Research Paper Review</h2><p>Structured findings grounded in the paper's retrieved evidence.</p></div><span className="review-status"><span className="status-dot" /> Analysis complete</span></div><div className="review-grid">{reviewSections.map(([key, title], index) => <ReviewCard key={key} title={title} data={review[key] || {}} isOverall={index === reviewSections.length - 1} />)}</div></section>}
      <footer className="footer"><span>Academic Review Workspace</span><span>Built for rigorous reading</span></footer>
    </main>
  );
}

export default App;