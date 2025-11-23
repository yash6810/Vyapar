import React from 'react';

// A simple card for displaying monthly summaries, styled to fit the new UI
export default function SummaryCard({ data }) {
  const breakdown = data.categoryBreakdown || {};
  return (
    <div className="summary-card" style={{ padding: '10px', border: '1px solid #eee', borderRadius: '8px', background: '#f9f9f9' }}>
      <h4 style={{ marginTop: 0, marginBottom: '10px', borderBottom: '1px solid #ddd', paddingBottom: '8px' }}>{data.title}</h4>
      <div style={{ marginBottom: '8px' }}>
        <strong>Total Spend:</strong> {data.totalSpend}
      </div>
      <div style={{ marginBottom: '8px' }}>
        <strong>GST Input:</strong> {data.gstInput}
      </div>
      <div style={{ marginBottom: '8px' }}>
        <strong>Top Vendors:</strong> {data.topVendors?.join(', ')}
      </div>
      <div>
        <strong>Breakdown:</strong>
        <ul style={{ margin: 0, paddingLeft: '20px' }}>
          {Object.entries(breakdown).map(([category, amount]) => (
            <li key={category}>{category}: {amount}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}
