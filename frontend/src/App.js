import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import Login from './components/Login';
import Register from './components/Register';
import Chat from './components/Chat';
import Dashboard from './components/Dashboard';
import './App.css';

function ProtectedRoute({ children, token }) {
  if (!token) return <Navigate to="/login" replace />;
  return children;
}

function AppRoutes() {
  const [token, setToken] = useState(localStorage.getItem('token'));
  const navigate = useNavigate();

  useEffect(() => {
    const handleStorage = () => setToken(localStorage.getItem('token'));
    window.addEventListener('storage', handleStorage);
    return () => window.removeEventListener('storage', handleStorage);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken(null);
    navigate('/login');
  };

  return (
    <div className="App">
      <Routes>
        <Route path="/login" element={
          token ? <Navigate to="/chat" replace /> : <Login setToken={setToken} />
        } />
        <Route path="/register" element={
          token ? <Navigate to="/chat" replace /> : <Register />
        } />
        <Route path="/chat" element={
          <ProtectedRoute token={token}>
            <Chat handleLogout={handleLogout} />
          </ProtectedRoute>
        } />
        <Route path="/dashboard" element={
          <ProtectedRoute token={token}>
            <Dashboard handleLogout={handleLogout} />
          </ProtectedRoute>
        } />
        <Route path="/" element={<Navigate to={token ? "/chat" : "/login"} replace />} />
      </Routes>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AppRoutes />
    </BrowserRouter>
  );
}
