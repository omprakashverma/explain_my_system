import React from 'react';
import { RepositorySummary } from '../repository/RepositorySummary';

export function Header({ busyMessage, onLogout, summary, user }) {
  return (
    <header className="hero-card">
      <div>
        <div className="hero-topbar">
          <p className="hero-kicker">Explain My System</p>
          <div className="auth-badge-row">
            <span className="chip">Signed in as {user?.username}</span>
            <button className="btn ghost" type="button" onClick={onLogout}>
              Logout
            </button>
          </div>
        </div>
        <h1>AI for codebase understanding</h1>
        <p className="hero-copy">
          Modern codebases are complex, distributed, and hard to understand. Explain My System
          helps developers interact with any repository in natural language to quickly understand
          architecture, dependencies, and behavior.
        </p>
      </div>

      <RepositorySummary summary={summary} busyMessage={busyMessage} />
    </header>
  );
}
