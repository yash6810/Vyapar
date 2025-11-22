import React, { useEffect } from 'react';
import { Form, Input, Button, DatePicker, InputNumber } from 'antd';
import moment from 'moment';

function InvoiceForm({ invoice, onSubmit }) {
  const [form] = Form.useForm();

  useEffect(() => {
    if (invoice) {
      form.setFieldsValue({
        ...invoice,
        date: invoice.date ? moment(invoice.date) : null,
      });
    } else {
      form.resetFields();
    }
  }, [invoice, form]);

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
        name="customer_name"
        label="Customer Name"
        rules={[{ required: true, message: 'Please enter a customer name!' }]}
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
          {invoice ? 'Update Invoice' : 'Create Invoice'}
        </Button>
      </Form.Item>
    </Form>
  );
}

export default InvoiceForm;
