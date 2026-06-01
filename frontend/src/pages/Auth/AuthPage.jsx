import React, { useState } from 'react';
import { useAuthContext } from '../../context/AuthContext';

const INITIAL_LOGIN_FORM = {
  username: '',
  password: ''
};

const INITIAL_REGISTER_FORM = {
  username: '',
  email: '',
  password: ''
};

export function AuthPage() {
  const { authBusy, authError, authView, login, register, setAuthError, setAuthView } =
    useAuthContext();
  const [loginForm, setLoginForm] = useState(INITIAL_LOGIN_FORM);
  const [registerForm, setRegisterForm] = useState(INITIAL_REGISTER_FORM);

  const handleLogin = async (event) => {
    event.preventDefault();
    try {
      await login(loginForm);
    } catch (error) {
      return error;
    }
  };

  const handleRegister = async (event) => {
    event.preventDefault();
    try {
      await register(registerForm);
    } catch (error) {
      return error;
    }
  };

  const switchView = (view) => {
    setAuthError('');
    setAuthView(view);
  };

  return (
    <main className="auth-shell">
      <section className="auth-card">
        <div className="auth-copy">
          <p className="hero-kicker">CodeAtlas</p>
          <h1>Secure access for repository analysis</h1>
          <p className="hero-copy">
            Sign in to explore repositories, ask architecture questions, and attach notes to files
            under your own account.
          </p>
          <div className="chip-row">
            <span className="chip">Private sessions</span>
            <span className="chip subtle">Hashed passwords</span>
            <span className="chip subtle">Admin auto-seeded</span>
          </div>
        </div>

        <div className="auth-panel">
          <div className="auth-toggle">
            <button
              className={`auth-tab ${authView === 'login' ? 'active' : ''}`}
              onClick={() => switchView('login')}
              type="button"
            >
              Login
            </button>
            <button
              className={`auth-tab ${authView === 'register' ? 'active' : ''}`}
              onClick={() => switchView('register')}
              type="button"
            >
              Register
            </button>
          </div>

          {authError ? (
            <div className="message-stack error">
              <p>{authError}</p>
            </div>
          ) : null}

          {authView === 'login' ? (
            <form className="auth-form" onSubmit={handleLogin}>
              <label className="auth-field">
                <span>Username</span>
                <input
                  className="text-input"
                  value={loginForm.username}
                  onChange={(event) =>
                    setLoginForm((current) => ({ ...current, username: event.target.value }))
                  }
                  placeholder="Enter your username"
                />
              </label>

              <label className="auth-field">
                <span>Password</span>
                <input
                  className="text-input"
                  type="password"
                  value={loginForm.password}
                  onChange={(event) =>
                    setLoginForm((current) => ({ ...current, password: event.target.value }))
                  }
                  placeholder="Enter your password"
                />
              </label>

              <button
                className="btn"
                type="submit"
                disabled={Boolean(authBusy) || !loginForm.username.trim() || !loginForm.password}
              >
                {authBusy || 'Login'}
              </button>
            </form>
          ) : (
            <form className="auth-form" onSubmit={handleRegister}>
              <label className="auth-field">
                <span>Username</span>
                <input
                  className="text-input"
                  value={registerForm.username}
                  onChange={(event) =>
                    setRegisterForm((current) => ({ ...current, username: event.target.value }))
                  }
                  placeholder="Choose a username"
                />
              </label>

              <label className="auth-field">
                <span>Email (optional)</span>
                <input
                  className="text-input"
                  type="email"
                  value={registerForm.email}
                  onChange={(event) =>
                    setRegisterForm((current) => ({ ...current, email: event.target.value }))
                  }
                  placeholder="you@example.com"
                />
              </label>

              <label className="auth-field">
                <span>Password</span>
                <input
                  className="text-input"
                  type="password"
                  value={registerForm.password}
                  onChange={(event) =>
                    setRegisterForm((current) => ({ ...current, password: event.target.value }))
                  }
                  placeholder="Create a password"
                />
              </label>

              <button
                className="btn"
                type="submit"
                disabled={Boolean(authBusy) || !registerForm.username.trim() || !registerForm.password}
              >
                {authBusy || 'Create account'}
              </button>
            </form>
          )}

          <p className="auth-footnote">
            Admin access is available for demos with username <strong>admin</strong>.
          </p>
        </div>
      </section>
    </main>
  );
}
