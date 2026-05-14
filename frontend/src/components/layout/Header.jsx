import React from 'react';
import { RepositorySummary } from '../repository/RepositorySummary';

export function Header({ summary, busyMessage }) {
  return (
    <header className="hero-card">
      <div>
        <p className="hero-kicker">Explain My System</p>
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
