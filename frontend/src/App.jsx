import React, { useEffect, useState, useRef } from "react";
import axios from "axios";

const API_BASE = "http://localhost:8002";

export default function App() {
  const [files, setFiles] = useState([]);
  const [summary, setSummary] = useState(null);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileContents, setFileContents] = useState({});
  const [loading, setLoading] = useState(false);
  const [gitUrl, setGitUrl] = useState("");

  const [username, setUsername] = useState("");
  const [fileQuestion, setFileQuestion] = useState("");
  const [taggedQuestions, setTaggedQuestions] = useState([]);

  const fileInputRef = useRef(null);

  const refresh = async () => {
    try {
      const r1 = await axios.get(`${API_BASE}/files`);
      const filesList = r1.data.files || [];
      setFiles(filesList);

      const contents = {};

      await Promise.all(
        filesList.map(async (path) => {
          try {
            const r = await axios.get(`${API_BASE}/file`, {
              params: { path },
            });

            contents[path] = r.data.text;
          } catch (err) {
            contents[path] = "Could not load file";
          }
        }),
      );

      setFileContents(contents);

      const r2 = await axios.get(`${API_BASE}/summary`);
      setSummary(r2.data);
    } catch (e) {
      console.error("refresh failed", e);
    }
  };

  useEffect(() => {
    refresh();
  }, []);

  const uploadZip = async (file) => {
    if (!file) return;

    const fd = new FormData();
    fd.append("file", file);

    setLoading(true);

    await axios.post(`${API_BASE}/upload-zip`, fd, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });

    await refresh();
    setLoading(false);
  };

  const loadGit = async () => {
    if (!gitUrl) return;

    setLoading(true);

    await axios.post(`${API_BASE}/load-git`, null, {
      params: { url: gitUrl },
    });

    await refresh();
    setLoading(false);
  };

  const clearAll = async () => {
    await axios.post(`${API_BASE}/clear`);

    setFiles([]);
    setSummary(null);
    setSelectedFile(null);
    setFileContents({});
    setAnswer(null);
    setTaggedQuestions([]);

    await refresh();
  };

  // SINGLE FIXED FUNCTION
  const openFile = async (path) => {
    setSelectedFile(path);

    try {
      const r = await axios.get(`${API_BASE}/file`, {
        params: { path },
      });

      setFileContents((prev) => ({
        ...prev,
        [path]: r.data.text,
      }));

      setTaggedQuestions(r.data.questions || []);
    } catch (e) {
      console.error("openFile failed", e);
    }
  };

  const tagQuestionToFile = async () => {
    if (!selectedFile || !username || !fileQuestion) return;

    await axios.post(`${API_BASE}/tag-question`, {
      path: selectedFile,
      username,
      question: fileQuestion,
    });

    setFileQuestion("");
    await openFile(selectedFile);
  };

  const onAsk = async () => {
    setAnswer("Thinking...");

    try {
      const r = await axios.post(`${API_BASE}/ask`, {
        question,
      });

      setAnswer(r.data.answer);
    } catch (e) {
      setAnswer("Error: " + (e?.response?.data?.detail || e.message));
    }
  };

  return (
    <div className="ems-root" style={{ margin: "20px" }}>
      <header className="ems-header">
        <h1 style={{ marginBottom: "30px", fontSize: "34px" }}>
          Explain My System{" "}
        </h1>

        <div className="ems-actions">
          <input
            ref={fileInputRef}
            type="file"
            accept=".zip"
            style={{ display: "none" }}
            onChange={(e) => uploadZip(e.target.files[0])}
          />

          <button
            className="btn"
            onClick={() => fileInputRef.current?.click()}
            style={{ color: "#000", fontSize: "15px" }}
          >
            Upload ZIP
          </button>
          <input
            className="git-input"
            placeholder="Git URL"
            value={gitUrl}
            onChange={(e) => setGitUrl(e.target.value)}
            style={{
              border: "1px solid #d1d5db",
              width: "400px",
              padding: "10px 12px",
              marginRight: "10px",
            }}
          />

          <button
            className="btn success"
            onClick={loadGit}
            disabled={!gitUrl.trim()}
            style={{
              color: "#000",
              fontSize: "15px",
              opacity: !gitUrl.trim() ? 0.5 : 1,
              cursor: !gitUrl.trim() ? "not-allowed" : "pointer",
            }}
          >
            Load from Git
          </button>

          <button
            style={{ color: "#000", fontSize: "15px" }}
            className="btn danger"
            onClick={clearAll}
          >
            Clear
          </button>
        </div>
      </header>

      <div className="ems-body">
        {/* FILE LIST */}
        <aside className="ems-sidebar">
          <h4>Files</h4>

          <div className="ems-files">
            {files.length === 0 && <div className="muted">No files loaded</div>}

            {files.map((f) => (
              <div
                key={f}
                className={`ems-file ${f === selectedFile ? "active" : ""}`}
                onClick={() => openFile(f)}
                style={{ cursor: "pointer" }}
              >
                {f}
              </div>
            ))}
          </div>
        </aside>

        {/* PREVIEW */}
        <aside className="ems-preview">
          <h4>Preview {selectedFile ? `— ${selectedFile}` : ""}</h4>

          <pre className="file-preview">
            {selectedFile
              ? fileContents[selectedFile] || "Loading..."
              : "Select a file to preview its contents"}
          </pre>
        </aside>

        {/* MAIN PANEL */}
        <main
          className="ems-main"
          style={{
            padding: "16px",
            width: "850px",
          }}
        >
          {/* <section className="ems-summary">
            <h3>Summary</h3>

            <pre>
              {summary
                ? JSON.stringify(summary, null, 2)
                : "No summary available"}
            </pre>
          </section> */}

          {/* TAG QUESTION SECTION */}
          <section className="ems-ask">
            <div style={{ marginTop: "20px" }}>
              <h4>Tag Question to File</h4>

              <input
                placeholder="Enter your name"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                style={{
                  width: "50%",
                  padding: "12px 14px",
                  marginBottom: "12px",
                  border: "1px solid #d1d5db",
                  borderRadius: "8px",
                  fontSize: "14px",
                  outline: "none",
                  boxSizing: "border-box",
                  boxShadow: "0 1px 2px rgba(0,0,0,0.05)",
                }}
              />

              <textarea
                placeholder="Tag question about this file"
                value={fileQuestion}
                onChange={(e) => setFileQuestion(e.target.value)}
                style={{
                  width: "100%",
                  minHeight: "80px",
                  marginBottom: "10px",
                }}
              />
              <button
                onClick={tagQuestionToFile}
                className="btn"
                disabled={
                  !selectedFile && !username.trim() && !fileQuestion.trim()
                }
                style={{
                  color: "#000",
                  fontSize: "15px",
                  opacity: !fileQuestion.trim() && !username.trim() ? 0.5 : 1,
                  cursor:
                    !fileQuestion.trim() && !username.trim()
                      ? "not-allowed"
                      : "pointer",
                }}
              >
                Tag Question
              </button>

              <div style={{ marginTop: "16px" }}>
                <h4
                  style={{
                    marginBottom: "12px",
                  }}
                >
                  Tagged Questions
                </h4>

                {taggedQuestions.length === 0 ? (
                  <div
                    style={{
                      padding: "12px",
                      border: "1px solid #e5e7eb",
                      borderRadius: "8px",
                      color: "#6b7280",
                    }}
                  >
                    No tagged questions
                  </div>
                ) : (
                  taggedQuestions.map((q, idx) => (
                    <details
                      key={idx}
                      style={{
                        marginBottom: "10px",
                        border: "1px solid #d1d5db",
                        borderRadius: "8px",
                        padding: "10px",
                      }}
                    >
                      <summary
                        style={{
                          cursor: "pointer",
                          fontWeight: "600",
                        }}
                      >
                        {q.username}
                      </summary>

                      <div
                        style={{
                          marginTop: "10px",
                        }}
                      >
                        <p
                          style={{
                            margin: "0 0 8px 0",
                          }}
                        >
                          <b>User query:</b> {q.question}
                        </p>
                        <small
                          style={{
                            color: "#6b7280",
                          }}
                        >
                          {new Date(q.timestamp).toLocaleString()}
                        </small>
                      </div>
                    </details>
                  ))
                )}
              </div>
            </div>
          </section>

          {/* ASK PROJECT */}
          <section className="ems-ask" style={{ marginTop: "40px" }}>
            <h3>Ask about the project</h3>

            <textarea
              placeholder="Ask a question..."
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
            />

            <div className="ems-controls">
              <button
                className="btn"
                onClick={onAsk}
                disabled={!question.trim()}
                style={{
                  color: "#000",
                  fontSize: "15px",
                  opacity: !question.trim() ? 0.5 : 1,
                  cursor: !question.trim() ? "not-allowed" : "pointer",
                }}
              >
                Ask
              </button>

              <span className="muted">{loading ? "Processing..." : ""}</span>
            </div>

            <h4>Answer</h4>

            <pre
              className="ems-answer"
              style={{
                padding: "16px",
                width: "600px",
              }}
            >
              {answer || "No answer yet"}
            </pre>
          </section>
        </main>
      </div>
    </div>
  );
}
