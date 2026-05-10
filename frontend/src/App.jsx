import React, { useEffect, useRef, useState } from "react";
import axios from "axios";

const API_BASE = "http://localhost:8002";

const EMPTY_CONTRACT = {
  loaded: false,
  filename: null,
  title: null,
  version: null,
  openapi_version: null,
  path_count: 0,
  operation_count: 0,
  raw_text: "",
  operations: [],
  validation: {
    valid: false,
    errors: [],
    warnings: [],
  },
};

function getErrorMessage(error) {
  return (
    error?.response?.data?.detail ||
    error?.response?.data?.message ||
    error?.message ||
    "Something went wrong."
  );
}

function formatSeverity(severity) {
  return severity ? severity[0].toUpperCase() + severity.slice(1) : "Info";
}

function formatComparisonStatus(status) {
  const labels = {
    matched: "Matched",
    missing: "Missing",
    undocumented: "Undocumented",
  };

  return labels[status] || "Info";
}

export default function App() {
  const [files, setFiles] = useState([]);
  const [summary, setSummary] = useState(null);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileContents, setFileContents] = useState({});
  const [busyMessage, setBusyMessage] = useState("");
  const [gitUrl, setGitUrl] = useState("");
  const [username, setUsername] = useState("");
  const [fileQuestion, setFileQuestion] = useState("");
  const [taggedQuestions, setTaggedQuestions] = useState([]);
  const [contract, setContract] = useState(EMPTY_CONTRACT);
  const [contractValidation, setContractValidation] = useState(null);
  const [appError, setAppError] = useState("");
  const [answerLoading, setAnswerLoading] = useState(false);
  const [highlightedLine, setHighlightedLine] = useState(null);

  const fileInputRef = useRef(null);
  const contractInputRef = useRef(null);
  const highlightedLineRef = useRef(null);

  const selectedFileLoaded = selectedFile
    ? Object.prototype.hasOwnProperty.call(fileContents, selectedFile)
    : false;
  const selectedFileText =
    selectedFile && selectedFileLoaded ? fileContents[selectedFile] || "" : "";
  const selectedFileLines = selectedFileLoaded ? selectedFileText.split("\n") : [];
  const selectedFileLineCount = selectedFileLoaded ? selectedFileLines.length : 0;
  const contractLineCount = contract.raw_text
    ? contract.raw_text.split("\n").length
    : 0;
  const health = contractValidation?.health || null;
  const healthScore = health?.score || 0;
  const healthWidth = `${Math.max(0, Math.min(100, healthScore))}%`;

  const isBusy = Boolean(busyMessage);
  const canValidate =
    files.length > 0 &&
    contract.loaded &&
    contract.validation?.valid &&
    !isBusy;

  useEffect(() => {
    if (!selectedFile || !highlightedLine || !highlightedLineRef.current) {
      return;
    }

    highlightedLineRef.current.scrollIntoView({
      behavior: "smooth",
      block: "center",
    });
  }, [selectedFile, selectedFileText, highlightedLine]);

  const resetPreviewState = () => {
    setSelectedFile(null);
    setHighlightedLine(null);
    setFileContents({});
    setTaggedQuestions([]);
  };

  const refresh = async () => {
    try {
      const [filesResponse, summaryResponse, contractResponse] = await Promise.all([
        axios.get(`${API_BASE}/files`),
        axios.get(`${API_BASE}/summary`),
        axios.get(`${API_BASE}/contract`),
      ]);

      const filesList = filesResponse.data.files || [];
      setFiles(filesList);
      setSummary(summaryResponse.data || null);
      setContract(contractResponse.data || EMPTY_CONTRACT);

      if (selectedFile && !filesList.includes(selectedFile)) {
        setSelectedFile(null);
        setHighlightedLine(null);
        setTaggedQuestions([]);
      }
    } catch (error) {
      console.error("refresh failed", error);
      setAppError(getErrorMessage(error));
    }
  };

  useEffect(() => {
    refresh();
  }, []);

  const runWithBusy = async (message, task) => {
    setBusyMessage(message);
    setAppError("");

    try {
      await task();
    } catch (error) {
      setAppError(getErrorMessage(error));
    } finally {
      setBusyMessage("");
    }
  };

  const uploadZip = async (file) => {
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    await runWithBusy("Uploading repository ZIP...", async () => {
      await axios.post(`${API_BASE}/upload-zip`, formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      setContractValidation(null);
      resetPreviewState();
      await refresh();
    });

    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const uploadContract = async (file) => {
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    await runWithBusy("Uploading OpenAPI contract...", async () => {
      const response = await axios.post(`${API_BASE}/upload-contract`, formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      setContract(response.data || EMPTY_CONTRACT);
      setContractValidation(null);
      await refresh();
    });

    if (contractInputRef.current) {
      contractInputRef.current.value = "";
    }
  };

  const loadGit = async () => {
    if (!gitUrl.trim()) return;

    await runWithBusy("Cloning repository from Git...", async () => {
      await axios.post(`${API_BASE}/load-git`, null, {
        params: { url: gitUrl.trim() },
      });

      setContractValidation(null);
      resetPreviewState();
      await refresh();
    });
  };

  const loadSampleRepo = async () => {
    await runWithBusy("Loading bundled sample API repo...", async () => {
      await axios.post(`${API_BASE}/load-sample`);
      setContractValidation(null);
      resetPreviewState();
      await refresh();
    });
  };

  const loadSampleContract = async () => {
    await runWithBusy("Loading bundled sample OpenAPI contract...", async () => {
      const response = await axios.post(`${API_BASE}/load-sample-contract`);
      setContract(response.data || EMPTY_CONTRACT);
      setContractValidation(null);
      await refresh();
    });
  };

  const validateContract = async () => {
    await runWithBusy("Validating repository against contract...", async () => {
      const response = await axios.post(`${API_BASE}/validate-contract`);
      setContractValidation(response.data);
    });
  };

  const clearAll = async () => {
    await runWithBusy("Clearing repository and contract state...", async () => {
      await axios.post(`${API_BASE}/clear`);

      setFiles([]);
      setSummary(null);
      setAnswer(null);
      setTaggedQuestions([]);
      setContract(EMPTY_CONTRACT);
      setContractValidation(null);
      setHighlightedLine(null);
      resetPreviewState();
      await refresh();
    });
  };

  const openFile = async (path, targetLine = null) => {
    setSelectedFile(path);
    setHighlightedLine(targetLine);
    setAppError("");

    try {
      const response = await axios.get(`${API_BASE}/file`, {
        params: { path },
      });

      setFileContents((current) => ({
        ...current,
        [path]: response.data.text,
      }));

      setTaggedQuestions(response.data.questions || []);
    } catch (error) {
      console.error("openFile failed", error);
      setAppError(getErrorMessage(error));
    }
  };

  const jumpToSource = async (path, line) => {
    if (!path) return;
    await openFile(path, line || null);
  };

  const tagQuestionToFile = async () => {
    if (!selectedFile || !username.trim() || !fileQuestion.trim()) return;

    await runWithBusy("Saving tagged question...", async () => {
      await axios.post(`${API_BASE}/tag-question`, {
        path: selectedFile,
        username: username.trim(),
        question: fileQuestion.trim(),
      });

      setFileQuestion("");
      await openFile(selectedFile, highlightedLine);
    });
  };

  const onAsk = async () => {
    if (!question.trim()) return;

    setAnswerLoading(true);
    setAppError("");
    setAnswer("Thinking...");

    try {
      const response = await axios.post(`${API_BASE}/ask`, {
        question: question.trim(),
      });

      setAnswer(response.data.answer);
    } catch (error) {
      setAnswer(`Error: ${getErrorMessage(error)}`);
    } finally {
      setAnswerLoading(false);
    }
  };

  const renderComparisonRows = () => {
    const rows = contractValidation?.comparison_rows || [];

    if (rows.length === 0) {
      return (
        <div className="empty-state">
          No route comparison rows are available yet. Run a validation to build the
          contract-versus-repository diff.
        </div>
      );
    }

    return (
      <div className="diff-table">
        <div className="diff-header">
          <span>Contract Route</span>
          <span>Repository Route</span>
          <span>Status</span>
          <span>Jump</span>
        </div>

        <div className="diff-body">
          {rows.map((row, index) => {
            const actionable = Boolean(row.clickable && row.source_file);
            const rowClassName = `diff-row ${row.status} ${actionable ? "actionable" : ""}`;
            const jumpLabel = actionable
              ? `${row.source_file}${row.source_line ? `:${row.source_line}` : ""}`
              : "No source link";

            const content = (
              <>
                <span className="diff-cell route">{row.contract_label}</span>
                <span className="diff-cell route">{row.repo_label}</span>
                <span className="diff-cell">
                  <span className={`status-badge ${row.status}`}>
                    {formatComparisonStatus(row.status)}
                  </span>
                </span>
                <span className="diff-cell jump">{jumpLabel}</span>
              </>
            );

            if (actionable) {
              return (
                <button
                  key={`${row.contract_label}-${row.repo_label}-${index}`}
                  type="button"
                  className={rowClassName}
                  onClick={() => jumpToSource(row.source_file, row.source_line)}
                >
                  {content}
                </button>
              );
            }

            return (
              <div
                key={`${row.contract_label}-${row.repo_label}-${index}`}
                className={rowClassName}
              >
                {content}
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  const renderContractValidation = () => {
    if (!contractValidation) {
      return (
        <div className="empty-state">
          Load a repository and an OpenAPI contract, then click `Validate Contract`
          to generate a health score, diff table, and actionable mismatch alerts.
        </div>
      );
    }

    return (
      <>
        <div className={`validation-banner ${contractValidation.status}`}>
          <div>
            <p className="section-kicker">Validation Status</p>
            <h3>{contractValidation.summary}</h3>
          </div>
          <div className="stat-grid compact">
            <div className="mini-stat">
              <span>Contract Ops</span>
              <strong>{contractValidation.counts?.contract_operations || 0}</strong>
            </div>
            <div className="mini-stat">
              <span>Repo Ops</span>
              <strong>{contractValidation.counts?.repo_operations || 0}</strong>
            </div>
            <div className="mini-stat">
              <span>Matched</span>
              <strong>{contractValidation.counts?.matched_operations || 0}</strong>
            </div>
            <div className="mini-stat">
              <span>Alerts</span>
              <strong>{contractValidation.counts?.alerts || 0}</strong>
            </div>
          </div>
        </div>

        {contractValidation.frameworks_detected?.length > 0 && (
          <div className="chip-row">
            {contractValidation.frameworks_detected.map((framework) => (
              <span key={framework} className="chip">
                {framework}
              </span>
            ))}
          </div>
        )}

        <section className="validation-section">
          <div className="section-head">
            <div>
              <p className="section-kicker">Side-by-Side Diff</p>
              <h3>Contract vs repository operations</h3>
            </div>
            <span className="section-hint">
              Click any row with a source path to jump directly into the matching code.
            </span>
          </div>
          {renderComparisonRows()}
        </section>

        <section className="validation-section">
          <div className="section-head">
            <div>
              <p className="section-kicker">Mismatch Alerts</p>
              <h3>Actionable findings</h3>
            </div>
            <span className="section-hint">
              Alerts with source links open the file preview at the relevant line.
            </span>
          </div>

          <div className="alert-list">
            {contractValidation.alerts?.length === 0 ? (
              <div className="empty-state success">
                No contract mismatches were detected in the loaded repository.
              </div>
            ) : (
              contractValidation.alerts.map((alert, index) => {
                const actionable = Boolean(alert.source_file);
                const cardClassName = `alert-card ${alert.severity} ${
                  actionable ? "actionable" : ""
                }`;
                const content = (
                  <>
                    <div className="alert-header">
                      <span className={`severity-pill ${alert.severity}`}>
                        {formatSeverity(alert.severity)}
                      </span>
                      <span className="alert-category">{alert.category}</span>
                    </div>
                    <p>{alert.message}</p>

                    {(alert.contract_path || alert.repo_path || alert.source_file) && (
                      <div className="alert-meta">
                        {alert.contract_path && (
                          <span>Contract path: {alert.contract_path}</span>
                        )}
                        {alert.repo_path && <span>Repo path: {alert.repo_path}</span>}
                        {alert.source_file && (
                          <span>
                            Click to open: {alert.source_file}
                            {alert.source_line ? ` line ${alert.source_line}` : ""}
                          </span>
                        )}
                      </div>
                    )}
                  </>
                );

                if (actionable) {
                  return (
                    <button
                      key={`${alert.category}-${index}`}
                      type="button"
                      className={cardClassName}
                      onClick={() => jumpToSource(alert.source_file, alert.source_line)}
                    >
                      {content}
                    </button>
                  );
                }

                return (
                  <article key={`${alert.category}-${index}`} className={cardClassName}>
                    {content}
                  </article>
                );
              })
            )}
          </div>
        </section>
      </>
    );
  };

  return (
    <div className="ems-root">
      <header className="hero-card">
        <div>
          <p className="hero-kicker">Smart API Contract Validator</p>
          <h1>Audit My System</h1>
          <p className="hero-copy">
            Upload a ZIP or clone a Git repo, attach an OpenAPI YAML or JSON
            contract, and compare detected API routes against the spec.
          </p>
        </div>

        <div className="stat-grid">
          <div className="stat-card">
            <span>Repository</span>
            <strong className="value-wrap">
              {summary?.source_label || "No repo loaded"}
            </strong>
            <small>{summary?.file_count || 0} files indexed</small>
          </div>
          <div className="stat-card">
            <span>Contract</span>
            <strong className="value-wrap">
              {contract.loaded ? contract.filename : "No contract"}
            </strong>
            <small>{contract.operation_count || 0} operations parsed</small>
          </div>
          <div className="stat-card health-stat">
            <span>Contract Health</span>
            <strong>{contractValidation ? `${healthScore}%` : "Awaiting run"}</strong>
            <div className="health-bar">
              <span className="health-bar-fill" style={{ width: healthWidth }} />
            </div>
            <small>
              {contractValidation
                ? `${health?.matched_operations || 0}/${health?.required_operations || 0} required operations matched`
                : "Run validation to calculate compliance"}
            </small>
          </div>
          <div className="stat-card">
            <span>Latest Validation</span>
            <strong>{contractValidation?.status || "Not run yet"}</strong>
            <small>{contractValidation?.counts?.alerts || 0} alerts</small>
          </div>
        </div>
      </header>

      <section className="control-grid">
        <article className="panel">
          <div className="panel-heading">
            <div>
              <p className="section-kicker">Repository Source</p>
              <h2>Load project code</h2>
            </div>
            {busyMessage && <span className="status-pill">{busyMessage}</span>}
          </div>

          <input
            ref={fileInputRef}
            type="file"
            accept=".zip"
            className="hidden-input"
            onChange={(event) => uploadZip(event.target.files?.[0])}
          />

          <div className="button-row">
            <button
              className="btn"
              onClick={() => fileInputRef.current?.click()}
              disabled={isBusy}
            >
              Upload ZIP
            </button>
            <button className="btn secondary" onClick={loadSampleRepo} disabled={isBusy}>
              Load Sample Repo
            </button>
            <button className="btn danger" onClick={clearAll} disabled={isBusy}>
              Clear All
            </button>
          </div>

          <div className="git-row">
            <input
              className="text-input"
              placeholder="https://github.com/example/api-repo.git"
              value={gitUrl}
              onChange={(event) => setGitUrl(event.target.value)}
            />
            <button
              className="btn ghost"
              onClick={loadGit}
              disabled={isBusy || !gitUrl.trim()}
            >
              Load from Git
            </button>
          </div>
        </article>

        <article className="panel">
          <div className="panel-heading">
            <div>
              <p className="section-kicker">OpenAPI Contract</p>
              <h2>Upload and validate</h2>
            </div>
            <span
              className={`status-pill ${contract.validation?.valid ? "valid" : "inactive"}`}
            >
              {contract.loaded
                ? contract.validation?.valid
                  ? "Contract ready"
                  : "Needs attention"
                : "No contract"}
            </span>
          </div>

          <input
            ref={contractInputRef}
            type="file"
            accept=".yaml,.yml,.json"
            className="hidden-input"
            onChange={(event) => uploadContract(event.target.files?.[0])}
          />

          <div className="button-row">
            <button
              className="btn"
              onClick={() => contractInputRef.current?.click()}
              disabled={isBusy}
            >
              Upload Contract
            </button>
            <button
              className="btn secondary"
              onClick={loadSampleContract}
              disabled={isBusy}
            >
              Load Sample Contract
            </button>
            <button className="btn ghost" onClick={validateContract} disabled={!canValidate}>
              Validate Contract
            </button>
          </div>

          <div className="chip-row">
            {contract.loaded ? (
              <>
                <span className="chip">{contract.filename}</span>
                {contract.openapi_version && (
                  <span className="chip">OpenAPI {contract.openapi_version}</span>
                )}
                <span className="chip">{contract.path_count || 0} paths</span>
                <span className="chip">{contract.operation_count || 0} operations</span>
              </>
            ) : (
              <span className="muted">
                Upload a YAML or JSON OpenAPI document to start validation.
              </span>
            )}
          </div>

          {contract.validation?.errors?.length > 0 && (
            <div className="message-stack error">
              {contract.validation.errors.map((item) => (
                <p key={item}>{item}</p>
              ))}
            </div>
          )}

          {contract.validation?.warnings?.length > 0 && (
            <div className="message-stack warning">
              {contract.validation.warnings.map((item) => (
                <p key={item}>{item}</p>
              ))}
            </div>
          )}
        </article>
      </section>

      {appError && (
        <section className="panel panel-alert">
          <p className="panel-alert-title">Action error</p>
          <p>{appError}</p>
        </section>
      )}

      <div className="ems-body">
        <aside className="panel ems-sidebar">
          <div className="panel-heading compact">
            <div>
              <p className="section-kicker">Repository Files</p>
              <h2>Source explorer</h2>
            </div>
          </div>

          <div className="ems-files">
            {files.length === 0 ? (
              <div className="empty-state">No repository files loaded yet.</div>
            ) : (
              files.map((filePath) => (
                <button
                  key={filePath}
                  type="button"
                  className={`ems-file ${filePath === selectedFile ? "active" : ""}`}
                  onClick={() => openFile(filePath)}
                >
                  {filePath}
                </button>
              ))
            )}
          </div>
        </aside>

        <aside className="panel ems-preview">
          <div className="panel-heading compact preview-heading">
            <div>
              <p className="section-kicker">File Preview</p>
              <h2>{selectedFile ? "Raw source view" : "Select a file"}</h2>
            </div>

            {selectedFile && (
              <div className="chip-row preview-meta">
                <span className="chip subtle">{selectedFile}</span>
                <span className="chip subtle">{selectedFileLineCount} lines</span>
                {highlightedLine && (
                  <span className="chip subtle">Line {highlightedLine}</span>
                )}
              </div>
            )}
          </div>

          <div className="preview-surface">
            <div className="preview-caption">
              {selectedFile
                ? highlightedLine
                  ? "A route-related line is highlighted below. Click other alerts or diff rows to jump again."
                  : "Click a mismatch alert or diff row with a source path to jump directly into the relevant code."
                : "Choose a file from the explorer to preview its source code here."}
            </div>

            <div className="file-preview">
              {!selectedFile ? (
                <div className="preview-empty">
                  Choose a file from the left panel to inspect its contents.
                </div>
              ) : !selectedFileLoaded ? (
                <div className="preview-empty">Loading file contents...</div>
              ) : (
                <div className="code-viewer">
                  {selectedFileLines.map((lineText, index) => {
                    const lineNumber = index + 1;
                    const isHighlighted = lineNumber === highlightedLine;

                    return (
                      <div
                        key={`${selectedFile}-${lineNumber}`}
                        className={`code-line ${isHighlighted ? "highlighted" : ""}`}
                        ref={isHighlighted ? highlightedLineRef : null}
                      >
                        <span className="code-line-number">{lineNumber}</span>
                        <code className="code-line-text">{lineText || " "}</code>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>
        </aside>

        <main className="ems-main">
          <section className="panel">
            <div className="panel-heading">
              <div>
                <p className="section-kicker">Validator Output</p>
                <h2>Contract mismatch alerts</h2>
              </div>
            </div>
            {renderContractValidation()}
          </section>

          <section className="panel">
            <div className="panel-heading preview-heading">
              <div>
                <p className="section-kicker">Contract Preview</p>
                <h2>{contract.title || "No contract loaded"}</h2>
              </div>

              {contract.loaded && (
                <div className="chip-row preview-meta">
                  <span className="chip subtle">{contract.filename}</span>
                  <span className="chip subtle">{contractLineCount} lines</span>
                  <span className="chip subtle">
                    {contract.operation_count || 0} operations
                  </span>
                </div>
              )}
            </div>

            <div className="preview-surface">
              <div className="preview-caption">
                {contract.loaded
                  ? "Raw OpenAPI contract preview with internal scrolling for long specs."
                  : "Load a contract to preview the uploaded OpenAPI document."}
              </div>

              <pre className="contract-preview">
                {contract.loaded
                  ? contract.raw_text
                  : "Load a contract to preview the uploaded OpenAPI document."}
              </pre>
            </div>
          </section>

          <section className="panel">
            <div className="panel-heading">
              <div>
                <p className="section-kicker">Collaborative Notes</p>
                <h2>Tag question to selected file</h2>
              </div>
            </div>

            <input
              className="text-input"
              placeholder="Your name"
              value={username}
              onChange={(event) => setUsername(event.target.value)}
            />

            <textarea
              className="text-area"
              placeholder="Tag a question about the selected file"
              value={fileQuestion}
              onChange={(event) => setFileQuestion(event.target.value)}
            />

            <div className="button-row">
              <button
                className="btn"
                onClick={tagQuestionToFile}
                disabled={
                  isBusy || !selectedFile || !username.trim() || !fileQuestion.trim()
                }
              >
                Save Question
              </button>
              <span className="muted">
                {selectedFile ? `Selected file: ${selectedFile}` : "No file selected"}
              </span>
            </div>

            <div className="tagged-list">
              {taggedQuestions.length === 0 ? (
                <div className="empty-state">No tagged questions for this file yet.</div>
              ) : (
                taggedQuestions.map((item, index) => (
                  <details key={`${item.username}-${index}`} className="tag-card">
                    <summary>{item.username}</summary>
                    <p>{item.question}</p>
                    <small>{new Date(item.timestamp).toLocaleString()}</small>
                  </details>
                ))
              )}
            </div>
          </section>

          <section className="panel">
            <div className="panel-heading">
              <div>
                <p className="section-kicker">Project Q and A</p>
                <h2>Ask about the loaded repository</h2>
              </div>
            </div>

            <textarea
              className="text-area"
              placeholder="Ask how the code works..."
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
            />

            <div className="button-row">
              <button
                className="btn"
                onClick={onAsk}
                disabled={answerLoading || !question.trim()}
              >
                Ask
              </button>
              <span className="muted">
                {answerLoading ? "Generating answer..." : "Uses the loaded code context"}
              </span>
            </div>

            <pre className="answer-box">{answer || "No answer yet."}</pre>
          </section>
        </main>
      </div>
    </div>
  );
}
