import React, { createContext, useContext, useEffect, useMemo, useState } from 'react';
import { authService } from '../services/authService';
import { authStorage } from '../services/authStorage';
import { getErrorMessage } from '../utils/errorUtils';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isAuthReady, setIsAuthReady] = useState(false);
  const [authError, setAuthError] = useState('');
  const [authBusy, setAuthBusy] = useState('');
  const [authView, setAuthView] = useState('login');

  useEffect(() => {
    let isMounted = true;

    const restoreSession = async () => {
      const token = authStorage.getToken();
      if (!token) {
        if (isMounted) {
          setIsAuthReady(true);
        }
        return;
      }

      try {
        const currentUser = await authService.getCurrentUser();
        if (isMounted) {
          setUser(currentUser);
        }
      } catch (error) {
        authStorage.clearToken();
        if (isMounted) {
          setAuthError(getErrorMessage(error));
        }
      } finally {
        if (isMounted) {
          setIsAuthReady(true);
        }
      }
    };

    restoreSession();
    return () => {
      isMounted = false;
    };
  }, []);

  const finishAuth = (payload) => {
    authStorage.setToken(payload.token);
    setUser(payload.user);
    setAuthError('');
  };

  const login = async (credentials) => {
    setAuthBusy('Signing you in...');
    setAuthError('');
    try {
      const payload = await authService.login(credentials);
      finishAuth(payload);
      return payload.user;
    } catch (error) {
      const message = getErrorMessage(error);
      setAuthError(message);
      throw error;
    } finally {
      setAuthBusy('');
    }
  };

  const register = async (details) => {
    setAuthBusy('Creating your account...');
    setAuthError('');
    try {
      const payload = await authService.register(details);
      finishAuth(payload);
      return payload.user;
    } catch (error) {
      const message = getErrorMessage(error);
      setAuthError(message);
      throw error;
    } finally {
      setAuthBusy('');
    }
  };

  const logout = async () => {
    setAuthBusy('Signing you out...');
    try {
      await authService.logout();
    } catch (error) {
      setAuthError(getErrorMessage(error));
    } finally {
      authStorage.clearToken();
      setUser(null);
      setAuthBusy('');
      setAuthView('login');
    }
  };

  const value = useMemo(
    () => ({
      authBusy,
      authError,
      authView,
      isAuthReady,
      isAuthenticated: Boolean(user),
      login,
      logout,
      register,
      setAuthError,
      setAuthView,
      user
    }),
    [authBusy, authError, authView, isAuthReady, user]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuthContext() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuthContext must be used within AuthProvider');
  }
  return context;
}
