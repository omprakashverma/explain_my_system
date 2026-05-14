import React from 'react';

export function RepositorySummary({ summary, busyMessage }) {
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
}
