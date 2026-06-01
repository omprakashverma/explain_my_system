import React from 'react';

const MENU_ITEMS = [
  { path: '/home', label: 'Home', shortLabel: 'H' },
  { path: '/questions', label: 'Questions', shortLabel: 'Q' },
  { path: '/dashboard', label: 'Dashboard', shortLabel: 'D' }
];

export function SidebarNavigation({ currentPath, onNavigate, onLogout, user }) {
  return (
    <aside className="app-sidebar">
      <div className="app-sidebar-brand">
        <div className="app-sidebar-logo">CA</div>
        <div>
          <p className="section-kicker">CodeAtlas</p>
          <h2>Workspace</h2>
        </div>
      </div>

      <nav className="app-sidebar-nav" aria-label="Primary">
        {MENU_ITEMS.map((item) => (
          <button
            key={item.path}
            className={`app-nav-item ${currentPath === item.path ? 'active' : ''}`}
            type="button"
            onClick={() => onNavigate(item.path)}
          >
            <span className="app-nav-icon" aria-hidden="true">{item.shortLabel}</span>
            <span>{item.label}</span>
          </button>
        ))}
      </nav>

      <div className="app-sidebar-footer">
        <div className="app-user-card">
          <span className="chip">Signed in</span>
          <strong>{user?.username || 'Unknown user'}</strong>
          <small>{user?.role || 'member'}</small>
        </div>

        <button className="btn ghost" type="button" onClick={onLogout}>
          Logout
        </button>
      </div>
    </aside>
  );
}
