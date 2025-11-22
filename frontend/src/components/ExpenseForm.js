import React, { useEffect } from 'react';
import { Form, Input, Button, DatePicker, InputNumber } from 'antd';
import moment from 'moment';

function ExpenseForm({ expense, onSubmit }) {
  const [form] = Form.useForm();

  useEffect(() => {
    if (expense) {
      form.setFieldsValue({
        ...expense,
        date: expense.date ? moment(expense.date) : null,
      });
    } else {
      form.resetFields();
    }
  }, [expense, form]);

  const onFinish = (values) => {
    onSubmit({
      ...values,
      date: values.date ? values.date.format('YYYY-MM-DD') : null,
    });
  };

  return (
    <Form form={form} layout="vertical" onFinish={onFinish}>
      <Form.Item
        name="date"
        label="Date"
        rules={[{ required: true, message: 'Please select a date!' }]}
      >
        <DatePicker />
      </Form.Item>
      <Form.Item
        name="item"
        label="Item"
        rules={[{ required: true, message: 'Please enter an item!' }]}
      >
        <Input />
      </Form.Item>
      <Form.Item
        name="amount"
        label="Amount"
        rules={[{ required: true, message: 'Please enter an amount!' }]}
      >
        <InputNumber min={0} />
      </Form.Item>
      <Form.Item>
        <Button type="primary" htmlType="submit">
          {expense ? 'Update Expense' : 'Create Expense'}
        </Button>
      </Form.Item>
    </Form>
  );
}

export default ExpenseForm;
