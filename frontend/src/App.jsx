import { useState } from "react";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [paperId, setPaperId] = useState("");
  const [message, setMessage] = useState("");
  const [review, setReview] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [reviewing, setReviewing] = useState(false);

  const uploadPaper = async () => {
    if (!file) {
      setMessage("Please select a PDF.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    setMessage("Uploading and indexing paper...");
    setReview(null);
    setUploading(true);

    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/upload`,
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        setMessage(data.error || "Upload failed.");
        return;
      }

      setPaperId(data.paper_id);

      setMessage(
        `Paper uploaded successfully. ${data.chunks_created} chunks created.`
      );
    } catch {
      setMessage("Could not connect to backend.");
    } finally {
      setUploading(false);
    }
  };

  const reviewPaper = async () => {
  if (!paperId) {
    setMessage("Upload a paper first.");
    return;
  }

  setReviewing(true);
  setMessage("AI agents are reviewing the paper...");
  setReview(null);

  try {
    const response = await fetch(
      `${import.meta.env.VITE_API_URL}/review`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          paper_id: paperId,
          query: "Review this research paper",
        }),
      }
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error(
        data.detail || "Review request failed."
      );
    }

    let parsedReview = data.review ?? data.final_review;

    if (!parsedReview) {
      throw new Error("The backend returned an empty review.");
    }

    if (typeof parsedReview === "string") {
      parsedReview = JSON.parse(parsedReview);
    }

    setReview(parsedReview);
    setMessage("Review completed successfully.");

  } catch (error) {
    console.error(error);

    setMessage(
      error.message || "Something went wrong while generating the review."
    );

  } finally {
    setReviewing(false);
  }
};

 return (
  <div className="app">

    <div className="header">
      <h1>AI Research Paper Reviewer</h1>
      <p>
        Upload a research paper and receive an evidence-based
        AI review.
      </p>
    </div>

   <div className="upload-card">

  <input
    type="file"
    accept=".pdf"
    onChange={(e) => setFile(e.target.files[0])}
  />

  <div>
    <button
      onClick={uploadPaper}
      disabled={uploading}
    >
      {uploading ? "Uploading..." : "Upload Paper"}
    </button>

    {paperId && (
      <button
        onClick={reviewPaper}
        disabled={reviewing}
      >
        {reviewing ? "Reviewing..." : "Review Paper"}
      </button>
    )}
  </div>

  <div className="status">
    <p>{message}</p>

    {reviewing && (
      <p>
        Methodology Agent → Novelty Agent → Quality Agent → Final Reviewer
      </p>
    )}
  </div>

</div>

    {review && (
      <div className="review-grid">

        {Object.entries(review).map(([section, data]) => (

          <div className="review-card" key={section}>

            <h3>
              {section
                .replaceAll("_", " ")
                .replace(/\b\w/g, (char) =>
                  char.toUpperCase()
                )}
            </h3>

            <p>{data.assessment}</p>

            <h4>Strengths</h4>

            <ul>
              {data.strengths?.map((item, index) => (
                <li key={index}>{item}</li>
              ))}
            </ul>

            <h4>Weaknesses</h4>

            <ul>
              {data.weaknesses?.map((item, index) => (
                <li key={index}>{item}</li>
              ))}
            </ul>

            <h4>Evidence</h4>

            {data.evidence?.map((item, index) => (
              <div className="evidence" key={index}>
                <strong>Page {item.page}</strong>
                <p>{item.text}</p>
              </div>
            ))}

          </div>

        ))}

      </div>
    )}

  </div>
);
}

export default App;