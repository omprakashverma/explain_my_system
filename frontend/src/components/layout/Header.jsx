import React from 'react';
import { RepositorySummary } from '../repository/RepositorySummary';

export function Header({ busyMessage, onLogout, summary, user }) {
  return (
    <header className="hero-card">
      <div>
        <div className="hero-topbar">
          <p className="hero-kicker">CodeAtlas</p>

          <div className="auth-badge-row">
            <span className="chip">Signed in as {user?.username}</span>

            <button
              className="btn ghost"
              type="button"
              onClick={onLogout}
            >
              Logout
            </button>
          </div>
        </div>

        <h1>Collaborative intelligence for codebases</h1>

        <p className="hero-copy">
          CodeAtlas helps developers explore repositories in natural language to
          understand architecture, dependencies, system behavior, and the
          engineering discussions behind the code. Ask questions, share knowledge,
          and collaborate around files or entire repositories — all in one place.
        </p>
      </div>

      <RepositorySummary
        summary={summary}
        busyMessage={busyMessage}
      />
    </header>
  );
}