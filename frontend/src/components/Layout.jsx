// ============================================================
//  src/components/Layout.js
//  THE APP SHELL — SIDEBAR + MAIN CONTENT AREA
//
//  Every page after login is wrapped in this Layout.
//  It provides:
//    - Sidebar with navigation links
//    - The user's name and role at the bottom of the sidebar
//    - A logout button
//    - The main content area where page components render
// ============================================================

import React from 'react';
import { NavLink, useNavigate, Outlet } from 'react-router-dom';
import {
  LayoutDashboard,
  MessageSquare,
  ClipboardList,
  BarChart2,
  Users,
  LogOut,
  BookOpen,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import"../styles/layout.css";
export default function Layout() {
  const { user, logout, isInstructor } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  // First letter of the user's name for the avatar circle
  const initials = user?.name?.charAt(0).toUpperCase() || '?';

  return (
    <div className="app-layout">
      {/* ── SIDEBAR ──────────────────────────────────────── */}
      <aside className="sidebar">
        {/* Brand */}
        <div className="sidebar-brand">
    <h2>🎓</h2>

    <h1>ITS</h1>

    <p>
        Intelligent<br />
        Tutoring System
    </p>
</div>

        {/* Navigation links */}
        <nav className="sidebar-nav">
          {/* Dashboard — different path for student vs instructor */}
          <NavLink
            to="/dashboard"
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          >
            <LayoutDashboard size={18} />
            Dashboard
          </NavLink>

          {/* Q&A Chatbot — students only */}
          {!isInstructor && (
            <NavLink
              to="/chatbot"
              className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
            >
              <MessageSquare size={18} />
              Q&A Chatbot
            </NavLink>
          )}

          {/* Quiz — students only */}
          {!isInstructor && (
            <NavLink
              to="/quiz"
              className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
            >
              <ClipboardList size={18} />
              Take a Quiz
            </NavLink>
          )}

          {/* Analytics — students see their own, instructors see class */}
          <NavLink
            to="/analytics"
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          >
            <BarChart2 size={18} />
            Analytics
          </NavLink>

          {/* Leaderboard — everyone */}
          <NavLink
            to="/leaderboard"
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          >
            <BookOpen size={18} />
            Leaderboard
          </NavLink>

          {/* Student list — instructors only */}
          {isInstructor && (
            <NavLink
              to="/students"
              className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
            >
              <Users size={18} />
              Students
            </NavLink>
          )}
        </nav>

        {/* User info + Logout at the bottom */}
        <div className="sidebar-footer">
          <div className="sidebar-user">
            <div className="avatar">{initials}</div>
            <div className="sidebar-user-info">
              <div className="name">{user?.name}</div>
              <div className="role">{user?.role}</div>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="btn btn-secondary btn-sm btn-block"
            style={{ gap: 8 }}
          >
            <LogOut size={15} />
            Log Out
          </button>
        </div>
      </aside>

      {/* ── MAIN CONTENT ─────────────────────────────────── */}
      {/* <Outlet /> renders whichever page component is currently active */}
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
}
