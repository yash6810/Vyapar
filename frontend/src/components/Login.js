import React, { useState } from 'react';
import { Form, Input, Button, message, Typography } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { Link } from 'react-router-dom';
import axios from 'axios';
import './Auth.css';

const { Title, Paragraph } = Typography;

function Login({ setToken }) {
  const [loading, setLoading] = useState(false);

  const onFinish = async (values) => {
    setLoading(true);
    try {
      const response = await axios.post('/token', new URLSearchParams(values).toString(), {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      });
      const { access_token } = response.data;
      localStorage.setItem('token', access_token);
      setToken(access_token);
    } catch (error) {
      message.error('Login failed: Invalid credentials');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <Title level={2} className="auth-title">Vyapar AI</Title>
        <Paragraph className="auth-subtitle">Welcome back! Please login to your account.</Paragraph>
        <Form
          name="login"
          onFinish={onFinish}
          className="auth-form"
          autoComplete="off"
        >
          <Form.Item
            name="username"
            rules={[{ required: true, message: 'Please input your email!' }]}
          >
            <Input prefix={<UserOutlined />} placeholder="Email" />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[{ required: true, message: 'Please input your password!' }]}
          >
            <Input.Password prefix={<LockOutlined />} placeholder="Password" />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} className="auth-button">
              Login
            </Button>
          </Form.Item>
          <Link to="/register" className="auth-link">Don't have an account? Register</Link>
        </Form>
      </div>
    </div>
  );
}

export default Login;
