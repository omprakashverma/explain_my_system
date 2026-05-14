import React from 'react';

export function AskPanel({ answer, answerLoading, onAsk, onQuestionChange, question }) {
  return (
    <section className="panel">
      <div className="panel-heading">
        <div>
          <p className="section-kicker">Project Question and Answer</p>
          <h2>Ask about the loaded repository</h2>
        </div>
      </div>

      <textarea
        className="text-area"
        placeholder="Ask how the code works..."
        value={question}
        onChange={(event) => onQuestionChange(event.target.value)}
      />

      <div className="button-row">
        <button className="btn" onClick={onAsk} disabled={answerLoading || !question.trim()}>
          Ask
        </button>
        <div className="muted" style={{ marginTop: '10px' }}>
          {answerLoading ? 'Generating answer...' : 'Uses the loaded code context'}
        </div>
      </div>

      <pre className="answer-box">{answer || 'No answer yet.'}</pre>
    </section>
  );
}
