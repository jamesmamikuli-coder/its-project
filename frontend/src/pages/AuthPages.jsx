// ============================================================
//  src/pages/LoginPage.js
//  LOGIN PAGE
// ============================================================

import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authAPI } from '../api/api';
import { useAuth } from '../context/AuthContext';

export function LoginPage() {
  const [email,    setEmail]    = useState('');
  const [password, setPassword] = useState('');
  const [error,    setError]    = useState('');
  const [loading,  setLoading]  = useState(false);

  const { login } = useAuth();
  const navigate  = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();   // Stop the browser from refreshing the page
    setError('');
    setLoading(true);

    try {
      const res = await authAPI.login(email, password);
      // Store token and user in context + localStorage
      login(res.data.token, res.data.user);
      // Redirect to the dashboard
      navigate('/dashboard');
    } catch (err) {
      // err.response.data.error is the message from Flask
      setError(err.response?.data?.error || 'Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-logo">
          <h1>🎓 ITS</h1>
          <p>Intelligent Tutoring System for Automated Question Answering and Student performance</p>
        </div>

        <h2 style={{ fontSize: 20, fontWeight: 700, marginBottom: 4 }}>Welcome back</h2>
        <p style={{ color: '#6b7280', fontSize: 14, marginBottom: 24 }}>
          Sign in to your account
        </p>

        {error && (
          <div className="alert alert-error">{error}</div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="email">Email address</label>
            <input
              id="email"
              type="email"
              className="form-control"
              value={email}
              onChange={e => setEmail(e.target.value)}
              placeholder="you@university.com"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              className="form-control"
              value={password}
              onChange={e => setPassword(e.target.value)}
              placeholder="Your password"
              required
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary btn-block btn-lg"
            disabled={loading}
            style={{ marginTop: 8 }}
          >
            {loading ? 'Signing in…' : 'Sign In'}
          </button>
        </form>

        <p style={{ textAlign: 'center', marginTop: 20, fontSize: 14, color: '#6b7280' }}>
          Don't have an account?{' '}
          <Link to="/register" style={{ fontWeight: 600 }}>Create one</Link>
        </p>
      </div>
    </div>
  );
}


// ============================================================
//  src/pages/RegisterPage.js
//  REGISTER PAGE
// ============================================================

export function RegisterPage() {
  const [form,    setForm]    = useState({ name: '', email: '', password: '', role: 'student' });
  const [errors,  setErrors]  = useState([]);
  const [loading, setLoading] = useState(false);

  const { login } = useAuth();
  const navigate  = useNavigate();

  const handleChange = (e) => {
    setForm(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrors([]);
    setLoading(true);

    try {
      const res = await authAPI.register(form.name, form.email, form.password, form.role);
      login(res.data.token, res.data.user);
      navigate('/dashboard');
    } catch (err) {
      const data = err.response?.data;
      if (data?.errors) {
        setErrors(data.errors);
      } else {
        setErrors([data?.error || 'Registration failed.']);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-logo">
          <h1>🎓 ITS</h1>
          <p>Intelligent Tutoring System</p>
        </div>

        <h2 style={{ fontSize: 20, fontWeight: 700, marginBottom: 4 }}>Create your account</h2>
        <p style={{ color: '#6b7280', fontSize: 14, marginBottom: 24 }}>
          Join the platform to start learning
        </p>

        {errors.length > 0 && (
          <div className="alert alert-error">
            {errors.map((e, i) => <div key={i}>{e}</div>)}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Full name</label>
            <input name="name" type="text" className="form-control"
              value={form.name} onChange={handleChange}
              placeholder="Mam Bello" required />
          </div>

          <div className="form-group">
            <label>Email address</label>
            <input name="email" type="email" className="form-control"
              value={form.email} onChange={handleChange}
              placeholder="you@university.com" required />
          </div>

          <div className="form-group">
            <label>Password <span style={{ fontWeight: 400, color: '#9ca3af' }}>(min 8 chars, include a number)</span></label>
            <input name="password" type="password" className="form-control"
              value={form.password} onChange={handleChange}
              placeholder="Choose a strong password" required />
          </div>

          <div className="form-group">
            <label>I am a…</label>
            <select name="role" className="form-control"
              value={form.role} onChange={handleChange}>
              <option value="student">Student</option>
              <option value="instructor">Instructor</option>
            </select>
          </div>

          <button type="submit" className="btn btn-primary btn-block btn-lg"
            disabled={loading} style={{ marginTop: 8 }}>
            {loading ? 'Creating account…' : 'Create Account'}
          </button>
        </form>

        <p style={{ textAlign: 'center', marginTop: 20, fontSize: 14, color: '#6b7280' }}>
          Already have an account?{' '}
          <Link to="/login" style={{ fontWeight: 600 }}>Sign in</Link>
        </p>
      </div>
    </div>
  );
}
