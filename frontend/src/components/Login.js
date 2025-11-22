import React, { useState } from 'react';
import axios from 'axios';

// A simple Login component styled to not interfere with the new CSS
function Login({ onLoginSuccess }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');

    // The /token endpoint expects form data, not JSON
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    try {
      const response = await axios.post('/token', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      });
      const { access_token } = response.data;
      onLoginSuccess(access_token);
    } catch (err) {
      if (err.response && err.response.status === 401) {
        setError('Incorrect username or password.');
      } else {
        setError('An error occurred. Please try again.');
      }
      console.error('Login failed:', err);
    }
  };

  const loginStyle = {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    height: '100vh',
    backgroundColor: '#e9edef',
  };

  const formStyle = {
    display: 'flex',
    flexDirection: 'column',
    gap: '15px',
    padding: '40px',
    borderRadius: '8px',
    backgroundColor: 'white',
    boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
    width: '320px',
  };
  
  const inputStyle = {
      padding: '10px',
      borderRadius: '5px',
      border: '1px solid #ccc'
  };

  const buttonStyle = {
      padding: '10px',
      borderRadius: '5px',
      border: 'none',
      backgroundColor: '#25D366',
      color: 'white',
      cursor: 'pointer',
      fontWeight: 'bold',
  };

  return (
    <div style={loginStyle}>
      <form onSubmit={handleLogin} style={formStyle}>
        <h2 style={{ textAlign: 'center', margin: 0, marginBottom: '20px' }}>VyaparAI Login</h2>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Email"
          required
          style={inputStyle}
        />
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Password"
          required
          style={inputStyle}
        />
        {error && <p style={{ color: 'red', textAlign: 'center', margin: 0 }}>{error}</p>}
        <button type="submit" style={buttonStyle}>Log In</button>
      </form>
    </div>
  );
}

export default Login;
