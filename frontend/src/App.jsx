import React, { useEffect, useRef, useState } from 'react';
import axios from 'axios';

const API_BASE = 'http://localhost:8002';

function getErrorMessage(error) {
  return (
    error?.response?.data?.detail ||
    error?.response?.data?.message ||
    error?.message ||
    'Something went wrong.'
  );
}

export default function App() {
  const [files, setFiles] = useState([]);
  const [summary, setSummary] = useState(null);
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileContents, setFileContents] = useState({});
  const [busyMessage, setBusyMessage] = useState('');
  const [gitUrl, setGitUrl] = useState('');
  const [username, setUsername] = useState('');
  const [fileQuestion, setFileQuestion] = useState('');
  const [taggedQuestions, setTaggedQuestions] = useState([]);
  const [appError, setAppError] = useState('');
  const [answerLoading, setAnswerLoading] = useState(false);
  const [highlightedLine, setHighlightedLine] = useState(null);

  const fileInputRef = useRef(null);
  const highlightedLineRef = useRef(null);

  const selectedFileLoaded = selectedFile
    ? Object.prototype.hasOwnProperty.call(fileContents, selectedFile)
    : false;

  const selectedFileText =
    selectedFile && selectedFileLoaded ? fileContents[selectedFile] || '' : '';

  const selectedFileLines = selectedFileLoaded ? selectedFileText.split('\n') : [];
  const selectedFileLineCount = selectedFileLoaded ? selectedFileLines.length : 0;

  const isBusy = Boolean(busyMessage);

  useEffect(() => {
    if (!selectedFile || !highlightedLine || !highlightedLineRef.current) {
      return;
    }

    highlightedLineRef.current.scrollIntoView({
      behavior: 'smooth',
      block: 'center'
    });
  }, [selectedFile, selectedFileText, highlightedLine]);

  const resetPreviewState = () => {
    setSelectedFile(null);
    setHighlightedLine(null);
    setFileContents({});
    setTaggedQuestions([]);
  };

  const runWithBusy = async (message, task) => {
    setBusyMessage(message);
    setAppError('');

    try {
      await task();
    } catch (error) {
      setAppError(getErrorMessage(error));
    } finally {
      setBusyMessage('');
    }
  };

  const refresh = async () => {
    try {
      const [filesResponse, summaryResponse] = await Promise.all([
        axios.get(`${API_BASE}/files`),
        axios.get(`${API_BASE}/summary`)
      ]);

      const filesList = filesResponse.data.files || [];
      setFiles(filesList);
      setSummary(summaryResponse.data || null);

      if (selectedFile && !filesList.includes(selectedFile)) {
        setSelectedFile(null);
        setHighlightedLine(null);
        setTaggedQuestions([]);
      }
    } catch (error) {
      console.error('refresh failed', error);
      setAppError(getErrorMessage(error));
    }
  };

  useEffect(() => {
    refresh();
  }, []);

  const uploadZip = async (file) => {
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    await runWithBusy('Uploading repository ZIP...', async () => {
      await axios.post(`${API_BASE}/upload-zip`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      resetPreviewState();
      await refresh();
    });

    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const loadGit = async () => {
    if (!gitUrl.trim()) return;

    await runWithBusy('Cloning repository from Git...', async () => {
      await axios.post(`${API_BASE}/load-git`, null, {
        params: { url: gitUrl.trim() }
      });

      resetPreviewState();
      await refresh();
    });
  };

  const loadSampleRepo = async () => {
    await runWithBusy('Loading bundled sample repository...', async () => {
      await axios.post(`${API_BASE}/load-sample`);
      resetPreviewState();
      await refresh();
    });
  };

  const clearAll = async () => {
    await runWithBusy('Clearing repository state...', async () => {
      await axios.post(`${API_BASE}/clear`);

      setFiles([]);
      setSummary(null);
      setAnswer(null);
      setTaggedQuestions([]);
      setHighlightedLine(null);
      resetPreviewState();
      await refresh();
    });
  };

  const openFile = async (path, targetLine = null) => {
    setSelectedFile(path);
    setHighlightedLine(targetLine);
    setAppError('');

    try {
      const response = await axios.get(`${API_BASE}/file`, {
        params: { path }
      });

      setFileContents((current) => ({
        ...current,
        [path]: response.data.text
      }));

      setTaggedQuestions(response.data.questions || []);
    } catch (error) {
      console.error('openFile failed', error);
      setAppError(getErrorMessage(error));
    }
  };

  const jumpToSource = async (path, line) => {
    if (!path) return;
    await openFile(path, line || null);
  };

  const tagQuestionToFile = async () => {
    if (!selectedFile || !username.trim() || !fileQuestion.trim()) return;

    await runWithBusy('Saving tagged question...', async () => {
      await axios.post(`${API_BASE}/tag-question`, {
        path: selectedFile,
        username: username.trim(),
        question: fileQuestion.trim()
      });

      setFileQuestion('');
      await openFile(selectedFile, highlightedLine);
    });
  };

 const onAsk = async () => {
  if (!question.trim()) return;

  setAnswerLoading(true);
  setAppError('');
  setAnswer('Thinking...');

  try {
    const response = await axios.post(`${API_BASE}/ask`, {
      prompt: question.trim(),
      selected_file: selectedFile || null
    });

    setAnswer(response.data.answer);
  } catch (error) {
    setAnswer(`Error: ${getErrorMessage(error)}`);
  } finally {
    setAnswerLoading(false);
  }
};

  const renderOverview = () => {
    const repoName = summary?.source_label || 'No repo loaded';
    const fileCount = summary?.file_count || 0;
    const languageCount = summary?.language_count || 0;
    const endpointCount = summary?.endpoint_count || 0;

    return (
      <div className="stat-grid">
        <div className="stat-card">
          <span>Repository</span>
          <strong className="value-wrap">{repoName}</strong>
          <small>{fileCount} files indexed</small>
        </div>

        <div className="stat-card">
          <span>Languages</span>
          <strong>{languageCount}</strong>
          <small>Detected in the repo</small>
        </div>

        <div className="stat-card">
          <span>API Routes</span>
          <strong>{endpointCount}</strong>
          <small>Endpoints discovered</small>
        </div>

        <div className="stat-card">
          <span>Latest Status</span>
          <strong>{summary?.status || 'Awaiting repo'}</strong>
          <small>{busyMessage || 'Ready to analyze'}</small>
        </div>
      </div>
    );
  };

  return (
    <div className="ems-root">
      <header className="hero-card">
        <div>
          <p className="hero-kicker">Explain My System</p>
          <h1>Understand the codebase faster</h1>
          <p className="hero-copy">
            Upload a ZIP or clone a Git repo, inspect the source tree, ask questions
            about the system, and jump directly to relevant files and lines.
          </p>
        </div>

        {renderOverview()}
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
              placeholder="https://github.com/example/repo.git"
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
              <p className="section-kicker">What the system is</p>
              <h2>Auto-generated project summary</h2>
            </div>
          </div>

          <div className="preview-surface">
            <div className="preview-caption">
              {summary?.overview ||
                'Load a repository to see a compact system overview, discovered modules, and other helpful metadata.'}
            </div>

            <div className="chip-row">
              {summary?.top_modules?.length > 0 ? (
                summary.top_modules.map((moduleName) => (
                  <span key={moduleName} className="chip">
                    {moduleName}
                  </span>
                ))
              ) : (
                <span className="muted">No modules detected yet.</span>
              )}
            </div>
          </div>
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
                  className={`ems-file ${filePath === selectedFile ? 'active' : ''}`}
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
              <h2>{selectedFile ? 'Raw source view' : 'Select a file'}</h2>
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
                  ? 'A relevant line is highlighted below. Click another alert, tag, or question to jump again.'
                  : 'Click a file from the explorer to inspect its code.'
                : 'Choose a file from the left panel to preview its contents.'}
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
                        className={`code-line ${isHighlighted ? 'highlighted' : ''}`}
                        ref={isHighlighted ? highlightedLineRef : null}
                      >
                        <span className="code-line-number">{lineNumber}</span>
                        <code className="code-line-text">{lineText || ' '}</code>
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
              <div className="muted" style={{ marginTop: '10px' }}>
                {answerLoading ? 'Generating answer...' : 'Uses the loaded code context'}
              </div>
            </div>

            <pre className="answer-box">{answer || 'No answer yet.'}</pre>
          </section>

          <section className="panel">
            <div className="panel-heading">
              <div>
                <p className="section-kicker">Collaborative Notes</p>
                <h2>Tag a question to the selected file</h2>
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
                {selectedFile ? `Selected file: ${selectedFile}` : 'No file selected'}
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
        </main>
      </div>
    </div>
  );
}