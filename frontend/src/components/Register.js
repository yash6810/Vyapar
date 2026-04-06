import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../api';
import './Auth.css';

export default function Register() {
  const [form, setForm] = useState({ email: '', password: '', confirmPassword: '', name: '', business_name: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (form.password !== form.confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    if (form.password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }

    setLoading(true);
    try {
      await api.post('/api/auth/register', {
        email: form.email,
        password: form.password,
        name: form.name || null,
        business_name: form.business_name || null,
      });
      setSuccess(true);
      setTimeout(() => navigate('/login'), 1500);
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed. Try a different email.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-logo">
          <div className="auth-logo-icon">₹</div>
        </div>
        <h1 className="auth-title text-gradient">Create Account</h1>
        <p className="auth-subtitle">Start managing your business finances with AI</p>

        {error && <div className="auth-error">{error}</div>}
        {success && <div className="auth-error" style={{ background: 'rgba(16,185,129,0.1)', borderColor: 'rgba(16,185,129,0.2)', color: 'var(--success)' }}>✅ Account created! Redirecting to login...</div>}

        <form className="auth-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Full Name</label>
            <input type="text" name="name" className="form-input" placeholder="Rahul Sharma" value={form.name} onChange={handleChange} />
          </div>
          <div className="form-group">
            <label>Business Name</label>
            <input type="text" name="business_name" className="form-input" placeholder="Sharma Traders Pvt Ltd" value={form.business_name} onChange={handleChange} />
          </div>
          <div className="form-group">
            <label>Email *</label>
            <input type="email" name="email" className="form-input" placeholder="you@business.com" value={form.email} onChange={handleChange} required autoFocus />
          </div>
          <div className="form-group">
            <label>Password *</label>
            <input type="password" name="password" className="form-input" placeholder="Min 6 characters" value={form.password} onChange={handleChange} required />
          </div>
          <div className="form-group">
            <label>Confirm Password *</label>
            <input type="password" name="confirmPassword" className="form-input" placeholder="••••••••" value={form.confirmPassword} onChange={handleChange} required />
          </div>
          <button type="submit" className="auth-btn" disabled={loading || success}>
            {loading ? 'Creating Account...' : 'Create Account'}
          </button>
        </form>

        <p className="auth-link">
          Already have an account? <Link to="/login">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
