import React, { useState } from 'react';
import { Form, Input, Button, message, Typography } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import './Auth.css';

const { Title, Paragraph } = Typography;

function Register() {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const onFinish = async (values) => {
    setLoading(true);
    try {
      await axios.post('/users/', { email: values.email, password: values.password });
      message.success('Registration successful! Please login.');
      navigate('/login');
    } catch (error) {
      message.error('Registration failed: Email may already be registered.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <Title level={2} className="auth-title">Create Account</Title>
        <Paragraph className="auth-subtitle">Join Vyapar AI and streamline your business.</Paragraph>
        <Form
          name="register"
          onFinish={onFinish}
          className="auth-form"
          autoComplete="off"
        >
          <Form.Item
            name="email"
            rules={[
                { type: 'email', message: 'The input is not valid E-mail!' },
                { required: true, message: 'Please input your E-mail!' }
            ]}
          >
            <Input prefix={<UserOutlined />} placeholder="Email" />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[{ required: true, message: 'Please input your password!' }]}
            hasFeedback
          >
            <Input.Password prefix={<LockOutlined />} placeholder="Password" />
          </Form.Item>

          <Form.Item
            name="confirm"
            dependencies={['password']}
            hasFeedback
            rules={[
              { required: true, message: 'Please confirm your password!' },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value || getFieldValue('password') === value) {
                    return Promise.resolve();
                  }
                  return Promise.reject(new Error('The two passwords that you entered do not match!'));
                },
              }),
            ]}
          >
            <Input.Password prefix={<LockOutlined />} placeholder="Confirm Password" />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} className="auth-button">
              Register
            </Button>
          </Form.Item>
          <Link to="/login" className="auth-link">Already have an account? Login</Link>
        </Form>
      </div>
    </div>
  );
}

export default Register;
