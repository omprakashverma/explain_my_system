import React from 'react';
import { EmptyState } from '../common/EmptyState';
import { formatTimestamp } from '../../utils/formatters';

function scopeLabel(scope) {
  return scope === 'REPOSITORY' ? 'Repository Question' : 'File Question';
}

export function NotesPanel({
  currentUser,
  discussionFilter,
  fileQuestion,
  isBusy,
  onDiscussionFilterChange,
  onFileQuestionChange,
  onQuestionScopeChange,
  onReplyChange,
  onResolveToggle,
  onSaveQuestion,
  onSubmitReply,
  questionScope,
  replyDrafts,
  selectedFile,
  teamName,
  taggedQuestions,
  onTeamNameChange,
  username
}) {
  return (
    <section className="panel">
      <div className="panel-heading">
        <div>
          <p className="section-kicker">Collaborative Notes</p>
          <h2>Tag file or repository questions</h2>
        </div>
      </div>

      <div className="preview-surface notes-toolbar">
        <span className="preview-caption">Signed in as {username}</span>

        <div className="scope-toggle">
          <button
            className={`scope-chip ${questionScope === 'FILE' ? 'active' : ''}`}
            type="button"
            onClick={() => onQuestionScopeChange('FILE')}
            disabled={!selectedFile}
          >
            File Tag
          </button>
          <button
            className={`scope-chip ${questionScope === 'REPOSITORY' ? 'active' : ''}`}
            type="button"
            onClick={() => onQuestionScopeChange('REPOSITORY')}
          >
            Repository Tag
          </button>
        </div>
      </div>

      <textarea
        className="text-area"
        placeholder={
          questionScope === 'FILE'
            ? 'Tag a question about the selected file'
            : 'Tag a question about the repository architecture or flow'
        }
        value={fileQuestion}
        onChange={(event) => onFileQuestionChange(event.target.value)}
      />

      <input
        className="text-input"
        type="text"
        placeholder="Optional team name, for example Platform or QA"
        value={teamName}
        onChange={(event) => onTeamNameChange(event.target.value)}
      />

      <div className="button-row">
        <button
          className="btn"
          onClick={onSaveQuestion}
          disabled={
            isBusy ||
            !username.trim() ||
            !fileQuestion.trim() ||
            (questionScope === 'FILE' && !selectedFile)
          }
        >
          Save Question
        </button>
        <span className="muted">
          {questionScope === 'FILE'
            ? selectedFile
              ? `Selected file: ${selectedFile}`
              : 'Select a file to create a file-level question.'
            : 'This question will be attached to the whole repository.'}
        </span>
      </div>

      <div className="scope-toggle">
        <button
          className={`scope-chip ${discussionFilter === 'ALL' ? 'active' : ''}`}
          type="button"
          onClick={() => onDiscussionFilterChange('ALL')}
        >
          All Discussions
        </button>
        <button
          className={`scope-chip ${discussionFilter === 'FILE' ? 'active' : ''}`}
          type="button"
          onClick={() => onDiscussionFilterChange('FILE')}
          disabled={!selectedFile}
        >
          File Discussions
        </button>
        <button
          className={`scope-chip ${discussionFilter === 'REPOSITORY' ? 'active' : ''}`}
          type="button"
          onClick={() => onDiscussionFilterChange('REPOSITORY')}
        >
          Repository Discussions
        </button>
      </div>

      <div className="tagged-list">
        {taggedQuestions.length === 0 ? (
          <EmptyState>
            {discussionFilter === 'REPOSITORY'
              ? 'No repository-wide questions yet.'
              : discussionFilter === 'FILE'
                ? 'No file-level questions for this file yet.'
                : 'No discussions available yet.'}
          </EmptyState>
        ) : (
          taggedQuestions.map((item) => {
            const canResolve = currentUser?.role === 'admin' || currentUser?.id === item.user_id;

            return (
              <article
                key={item.id}
                className={`tag-card discussion-card ${item.resolved ? 'resolved' : 'open'}`}
              >
                <div className="discussion-header">
                  <div>
                    <div className="chip-row">
                      <span className={`status-pill ${item.resolved ? 'valid' : 'inactive'}`}>
                        {item.resolved ? 'Resolved' : 'Open'}
                      </span>
                      <span className="chip subtle">{scopeLabel(item.scope)}</span>
                      {item.team_name ? <span className="chip subtle">Team: {item.team_name}</span> : null}
                      <span className="chip subtle">{item.reply_count} replies</span>
                    </div>
                    <h3 className="discussion-author">{item.username}</h3>
                    <small className="muted">{formatTimestamp(item.created_at)}</small>
                  </div>

                  {canResolve ? (
                    <button
                      className="btn ghost"
                      type="button"
                      onClick={() => onResolveToggle(item.id, item.resolved)}
                      disabled={isBusy}
                    >
                      {item.resolved ? 'Mark Unresolved' : 'Mark Resolved'}
                    </button>
                  ) : null}
                </div>

                {item.path ? <p className="muted">File: {item.path}</p> : null}

                <p className="discussion-question">{item.question}</p>

                {item.resolved_at ? (
                  <p className="muted">Resolved on {formatTimestamp(item.resolved_at)}</p>
                ) : null}

                <div className="reply-list">
                  {item.replies.length === 0 ? (
                    <p className="muted">No replies yet.</p>
                  ) : (
                    item.replies.map((reply) => (
                      <div key={reply.id} className="reply-card">
                        <div className="reply-meta">
                          <strong>{reply.username}</strong>
                          <small>{formatTimestamp(reply.created_at)}</small>
                        </div>
                        <p>{reply.content}</p>
                      </div>
                    ))
                  )}
                </div>

                <div className="reply-composer">
                  <textarea
                    className="text-area compact"
                    placeholder="Write a reply"
                    value={replyDrafts[item.id] || ''}
                    onChange={(event) => onReplyChange(item.id, event.target.value)}
                  />
                  <div className="button-row">
                    <button
                      className="btn primary"
                      type="button"
                      onClick={() => onSubmitReply(item.id)}
                      disabled={isBusy || !(replyDrafts[item.id] || '').trim()}
                    >
                      Reply
                    </button>
                    {item.latest_reply_at ? (
                      <span className="muted">
                        Latest reply {formatTimestamp(item.latest_reply_at)}
                      </span>
                    ) : null}
                  </div>
                </div>
              </article>
            );
          })
        )}
      </div>
    </section>
  );
}
