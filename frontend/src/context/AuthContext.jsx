// ============================================================
//  src/context/AuthContext.js
//  GLOBAL AUTHENTICATION STATE
//
//  React Context is a way to share state across many components
//  WITHOUT passing props through every level of the tree.
//
//  Example problem without Context:
//    App → Layout → Sidebar → NavItem
//  To pass "user" to NavItem, you'd need:
//    App passes user → Layout passes user → Sidebar passes user → NavItem uses user
//  That's called "prop drilling" — messy and hard to maintain.
//
//  With Context:
//    Any component can call useAuth() to get the user directly.
//    No prop drilling needed.
//
//  THIS FILE PROVIDES:
//    user      — the logged-in user object (or null if not logged in)
//    token     — the JWT token string
//    login()   — call this after successful login/register
//    logout()  — call this to log out
//    isStudent   — true if role === 'student'
//    isInstructor — true if role === 'instructor'
// ============================================================

import React, { createContext, useContext, useState, useEffect } from 'react';

// Step 1: Create the context object
// This is like creating a "radio station" that components can tune into
const AuthContext = createContext(null);

// ── PROVIDER COMPONENT ────────────────────────────────────────
// Wrap <AuthProvider> around the whole app so every component
// can access auth state via useAuth()
export function AuthProvider({ children }) {
  // Read stored user/token from localStorage on first render
  // This means the user stays logged in if they refresh the page
  const [user, setUser]   = useState(() => {
    try {
      const stored = localStorage.getItem('its_user');
      return stored ? JSON.parse(stored) : null;
    } catch { return null; }
  });

  const [token, setToken] = useState(() =>
    localStorage.getItem('its_token') || null
  );

  /**
   * Call this after a successful login or register.
   * Stores the token and user in both state and localStorage.
   *
   * @param {string} newToken - the JWT token from the server
   * @param {object} newUser  - the user profile object from the server
   */
  const login = (newToken, newUser) => {
    localStorage.setItem('its_token', newToken);
    localStorage.setItem('its_user', JSON.stringify(newUser));
    setToken(newToken);
    setUser(newUser);
  };

  /**
   * Call this to log the user out.
   * Clears token and user from both state and localStorage.
   * The axios interceptor will also call this if a 401 is received.
   */
  const logout = () => {
    localStorage.removeItem('its_token');
    localStorage.removeItem('its_user');
    setToken(null);
    setUser(null);
  };

  // Convenience flags — components check these instead of user.role === '...'
  const isStudent    = user?.role === 'student';
  const isInstructor = user?.role === 'instructor';
  const isLoggedIn   = !!token;

  // The value object is what all consumers get when they call useAuth()
  const value = {
    user,
    token,
    login,
    logout,
    isStudent,
    isInstructor,
    isLoggedIn,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

// ── CUSTOM HOOK ───────────────────────────────────────────────
// Components call useAuth() instead of useContext(AuthContext)
// This is cleaner and gives a better error message if used outside Provider
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth() must be used inside <AuthProvider>');
  }
  return context;
}
