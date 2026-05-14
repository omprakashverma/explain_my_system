import React from 'react';
import { EmptyState } from '../common/EmptyState';
import { formatTimestamp } from '../../utils/formatters';

export function NotesPanel({
  fileQuestion,
  isBusy,
  onFileQuestionChange,
  onSaveQuestion,
  onUsernameChange,
  selectedFile,
  taggedQuestions,
  username
}) {
  return (
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
        onChange={(event) => onUsernameChange(event.target.value)}
      />

      <textarea
        className="text-area"
        placeholder="Tag a question about the selected file"
        value={fileQuestion}
        onChange={(event) => onFileQuestionChange(event.target.value)}
      />

      <div className="button-row">
        <button
          className="btn"
          onClick={onSaveQuestion}
          disabled={isBusy || !selectedFile || !username.trim() || !fileQuestion.trim()}
        >
          Save Question
        </button>
        <span className="muted">{selectedFile ? `Selected file: ${selectedFile}` : 'No file selected'}</span>
      </div>

      <div className="tagged-list">
        {taggedQuestions.length === 0 ? (
          <EmptyState>No tagged questions for this file yet.</EmptyState>
        ) : (
          taggedQuestions.map((item, index) => (
            <details key={`${item.username}-${index}`} className="tag-card">
              <summary>{item.username}</summary>
              <p>{item.question}</p>
              <small>{formatTimestamp(item.timestamp)}</small>
            </details>
          ))
        )}
      </div>
    </section>
  );
}
