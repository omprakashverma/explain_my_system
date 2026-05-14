import React from 'react';

export function FilePreview({
  highlightedLine,
  highlightedLineRef,
  selectedFile,
  selectedFileLineCount,
  selectedFileLines,
  selectedFileLoaded
}) {
  return (
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
            {highlightedLine && <span className="chip subtle">Line {highlightedLine}</span>}
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
            <div className="preview-empty">Choose a file from the left panel to inspect its contents.</div>
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
  );
}
