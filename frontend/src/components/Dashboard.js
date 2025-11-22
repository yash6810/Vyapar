import React, { useState, useEffect } from 'react';
import { Table, Button, Space, Typography, message } from 'antd';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const { Title } = Typography;

function Dashboard() {
  const [expenses, setExpenses] = useState([]);
  const [invoices, setInvoices] = useState([]);
  const navigate = useNavigate();
  const token = localStorage.getItem('token');

  const fetchExpenses = async () => {
    try {
      const response = await axios.get('/expenses/', {
        headers: { Authorization: `Bearer ${token}` },
      });
      setExpenses(response.data);
    } catch (error) {
      message.error('Failed to fetch expenses');
    }
  };

  const fetchInvoices = async () => {
    try {
      const response = await axios.get('/invoices/', {
        headers: { Authorization: `Bearer ${token}` },
      });
      setInvoices(response.data);
    } catch (error) {
      message.error('Failed to fetch invoices');
    }
  };

  useEffect(() => {
    if (token) {
      fetchExpenses();
      fetchInvoices();
    }
  }, [token]);

  const handleDeleteExpense = async (id) => {
    try {
      await axios.delete(`/expenses/${id}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      message.success('Expense deleted successfully');
      fetchExpenses();
    } catch (error) {
      message.error('Failed to delete expense');
    }
  };

  const handleDeleteInvoice = async (id) => {
    try {
      await axios.delete(`/invoices/${id}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      message.success('Invoice deleted successfully');
      fetchInvoices();
    } catch (error) {
      message.error('Failed to delete invoice');
    }
  };

  const expenseColumns = [
    { title: 'Date', dataIndex: 'date', key: 'date' },
    { title: 'Item', dataIndex: 'item', key: 'item' },
    { title: 'Amount', dataIndex: 'amount', key: 'amount' },
    {
      title: 'Action',
      key: 'action',
      render: (_, record) => (
        <Space size="middle">
          <Button onClick={() => navigate(`/edit-expense/${record.id}`)}>Edit</Button>
          <Button danger onClick={() => handleDeleteExpense(record.id)}>Delete</Button>
        </Space>
      ),
    },
  ];

  const invoiceColumns = [
    { title: 'Date', dataIndex: 'date', key: 'date' },
    { title: 'Customer', dataIndex: 'customer_name', key: 'customer_name' },
    { title: 'Amount', dataIndex: 'amount', key: 'amount' },
    {
      title: 'Action',
      key: 'action',
      render: (_, record) => (
        <Space size="middle">
          <Button onClick={() => navigate(`/edit-invoice/${record.id}`)}>Edit</Button>
          <Button danger onClick={() => handleDeleteInvoice(record.id)}>Delete</Button>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Title level={2}>Dashboard</Title>
      <Space style={{ marginBottom: 16 }}>
        <Button type="primary" onClick={() => navigate('/create-expense')}>
          Create New Expense
        </Button>
        <Button type="primary" onClick={() => navigate('/create-invoice')}>
          Create New Invoice
        </Button>
      </Space>
      <Title level={3}>Expenses</Title>
      <Table columns={expenseColumns} dataSource={expenses} rowKey="id" />
      <Title level={3}>Invoices</Title>
      <Table columns={invoiceColumns} dataSource={invoices} rowKey="id" />
    </div>
  );
}

export default Dashboard;
