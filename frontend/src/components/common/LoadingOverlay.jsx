import React from 'react';

export function LoadingOverlay({ message }) {
  if (!message) return null;
  return (
    <div className="loading-overlay" aria-live="polite">
      <div className="loading-overlay-card">
        <p className="section-kicker">Working</p>
        <strong>{message}</strong>
      </div>
    </div>
  );
}
