import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Link, useNavigate } from 'react-router-dom';
import { ConfigProvider, theme } from 'antd';
import Login from './components/Login';
import Register from './components/Register';
import Chat from './components/Chat';
import './App.css';

function App() {
  const [token, setToken] = useState(localStorage.getItem('token'));
  const navigate = useNavigate();

  useEffect(() => {
    // Only redirect if the current path is not login or register
    if (token && (window.location.pathname === '/login' || window.location.pathname === '/register' || window.location.pathname === '/')) {
      navigate('/chat');
    } else if (!token && window.location.pathname !== '/register') {
      navigate('/login');
    }
  }, [token, navigate]);

  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken(null);
    navigate('/login');
  };

  return (
    <ConfigProvider theme={{ algorithm: theme.darkAlgorithm }}>
      <div className="App">
        <Routes>
          <Route path="/login" element={<Login setToken={setToken} />} />
          <Route path="/register" element={<Register />} />
          {token && <Route path="/chat" element={<Chat handleLogout={handleLogout} />} />}
          <Route path="/" element={token ? <Chat handleLogout={handleLogout} /> : <Login setToken={setToken} />} />
        </Routes>
      </div>
    </ConfigProvider>
  );
}

function AppWrapper() {
  return (
    <BrowserRouter>
      <App />
    </BrowserRouter>
  );
}

export default AppWrapper;
