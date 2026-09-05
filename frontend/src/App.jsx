import { useState } from "react";

function App() {
  const [file, setFile] = useState(null);
  const [paperId, setPaperId] = useState("");
  const [message, setMessage] = useState("");
  const [review, setReview] = useState(null);

  const uploadPaper = async () => {
    if (!file) {
      setMessage("Please select a PDF.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    setMessage("Uploading and indexing paper...");
    setReview(null);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/upload",
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
    } catch (error) {
      setMessage("Could not connect to backend.");
    }
  };

  const reviewPaper = async () => {
    if (!paperId) {
      setMessage("Upload a paper first.");
      return;
    }

    setMessage("AI agents are reviewing the paper...");
    setReview(null);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/review",
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
        setMessage("Review failed.");
        return;
      }

      let parsedReview = data.review;

      if (typeof parsedReview === "string") {
        parsedReview = JSON.parse(parsedReview);
      }

      setReview(parsedReview);
      setMessage("Review completed.");
    } catch (error) {
      console.error(error);
      setMessage("Could not generate review.");
    }
  };

  return (
    <div>
      <h1>AI Research Paper Reviewer</h1>

      <p>
        Upload a research paper and get an AI-powered review.
      </p>

      <input
        type="file"
        accept=".pdf"
        onChange={(e) => setFile(e.target.files[0])}
      />

      <button onClick={uploadPaper}>
        Upload Paper
      </button>

      {paperId && (
        <button onClick={reviewPaper}>
          Review Paper
        </button>
      )}

      <p>{message}</p>

      {review && (
        <div>
          <h2>Research Review</h2>

          {Object.entries(review).map(([section, data]) => (
            <div key={section}>
              <h3>
                {section.replaceAll("_", " ").toUpperCase()}
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
              <ul>
                {data.evidence?.map((item, index) => (
                  <li key={index}>
                    <strong>Page {item.page}:</strong>{" "}
                    {item.text}
                  </li>
                ))}
              </ul>

              <hr />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default App;