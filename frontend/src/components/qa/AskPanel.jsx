import React from 'react';
import { AnswerRenderer } from './AnswerRenderer';

export function AskPanel({
  answer,
  answerLoading,
  askScope,
  onAsk,
  onQuestionChange,
  onScopeChange,
  question,
  selectedFile
}) {
  return (
    <section className="panel">
      <div className="panel-heading">
        <div>
          <p className="section-kicker">Project Question and Answer</p>
          <h2>Ask about the loaded repository</h2>
        </div>
      </div>

      <div className="scope-toggle">
        <button
          className={`scope-chip ${askScope === 'FILE' ? 'active' : ''}`}
          type="button"
          onClick={() => onScopeChange('FILE')}
          disabled={!selectedFile}
        >
          Ask Current File
        </button>
        <button
          className={`scope-chip ${askScope === 'REPOSITORY' ? 'active' : ''}`}
          type="button"
          onClick={() => onScopeChange('REPOSITORY')}
        >
          Ask Entire Repository
        </button>
      </div>

      <div className="preview-surface">
        <span className="preview-caption">
          {askScope === 'FILE'
            ? selectedFile
              ? `Using focused file context from ${selectedFile}`
              : 'Select a file to use file scope.'
            : 'Using repository summary, tree, and relevant files from the whole codebase.'}
        </span>
      </div>

      <textarea
        className="text-area"
        placeholder={
          askScope === 'FILE'
            ? 'Ask how the selected file works...'
            : 'Ask how the repository architecture, flow, or dependencies work...'
        }
        value={question}
        onChange={(event) => onQuestionChange(event.target.value)}
      />

      <div className="button-row">
        <button
          className="btn"
          onClick={onAsk}
          disabled={answerLoading || !question.trim() || (askScope === 'FILE' && !selectedFile)}
        >
          Ask
        </button>
        <div className="muted ask-hint">
          {answerLoading
            ? 'Generating answer...'
            : askScope === 'FILE'
              ? 'Uses the selected file plus nearby chunks'
              : 'Uses repository-wide retrieval across relevant files'}
        </div>
      </div>

      <AnswerRenderer answer={answer} />
    </section>
  );
}
