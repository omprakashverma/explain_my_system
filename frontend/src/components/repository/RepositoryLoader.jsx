import React from 'react';

export function RepositoryLoader({
  busyMessage,
  fileInputRef,
  gitUrl,
  isBusy,
  onClearAll,
  onGitUrlChange,
  onLoadGit,
  onLoadSampleRepo,
  onUploadZip
}) {
  return (
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
        onChange={(event) => onUploadZip(event.target.files?.[0])}
      />

      <div className="button-row">
        <button className="btn" onClick={() => fileInputRef.current?.click()} disabled={isBusy}>
          Upload ZIP
        </button>
        <button className="btn secondary" onClick={onLoadSampleRepo} disabled={isBusy}>
          Load Sample Repo
        </button>
        <button className="btn danger" onClick={onClearAll} disabled={isBusy}>
          Clear All
        </button>
      </div>

      <div className="git-row">
        <input
          className="text-input"
          placeholder="https://github.com/example/repo.git"
          value={gitUrl}
          onChange={(event) => onGitUrlChange(event.target.value)}
        />
        <button className="btn ghost" onClick={onLoadGit} disabled={isBusy || !gitUrl.trim()}>
          Load from Git
        </button>
      </div>
    </article>
  );
}
