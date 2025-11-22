import React from 'react';
import './SummaryCard.css';

function SummaryCard({ data }) {
  return (
    <div className="summary-card">
      <div className="summary-card-header">
        {data.title}
      </div>
      <div className="summary-card-body">
        <div className="summary-item">
          <span className="summary-label">Total Spend:</span>
          <span className="summary-value">{data.totalSpend}</span>
        </div>
        <div className="summary-item">
          <span className="summary-label">Top Vendors:</span>
          <ul className="summary-list">
            {data.topVendors.map((vendor, index) => (
              <li key={index}>{vendor}</li>
            ))}
          </ul>
        </div>
        <div className="summary-item">
          <span className="summary-label">GST Input:</span>
          <span className="summary-value">{data.gstInput}</span>
        </div>
        <div className="summary-item">
          <span className="summary-label">Category Breakdown:</span>
          <ul className="summary-list">
            {Object.entries(data.categoryBreakdown).map(([category, amount]) => (
              <li key={category}>{category}: {amount}</li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}

export default SummaryCard;
