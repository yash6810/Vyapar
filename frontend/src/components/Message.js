import React from 'react';
import SummaryCard from './SummaryCard'; // We will create this next

export default function Message({ msg, onConfirm }) {
  const isUser = msg.from === 'user';
  const cls = isUser ? 'msg user' : 'msg bot';

  const renderContent = () => {
    switch (msg.type) {
      case 'image':
        return <img src={msg.src} alt="Uploaded content" className="message-image" style={{ maxWidth: '300px', borderRadius: '8px' }} />;
      
      case 'summary_card':
        return <SummaryCard data={msg.data} />;

      case 'confirmation':
        return (
          <div className="confirmation-card">
            <div className="confirmation-header">Extracted Data</div>
            <div className="confirmation-body">
              {Object.entries(msg.data).map(([key, value]) => (
                <div key={key} className="confirmation-item">
                  <span className="confirmation-label" style={{ fontWeight: 'bold', marginRight: '8px' }}>{key}:</span>
                  <span className="confirmation-value">{value}</span>
                </div>
              ))}
            </div>
            <div className="confirmation-buttons" style={{ marginTop: '12px' }}>
              <button onClick={() => onConfirm('confirm', msg.data)} style={{ marginRight: '8px' }}>Confirm</button>
              <button onClick={() => onConfirm('retry', msg.data)}>Retry</button>
            </div>
          </div>
        );

      default: // 'text' and undefined
        return msg.text;
    }
  };

  return (
    <div className={cls}>
      <div className="bubble">
        {renderContent()}
      </div>
      <div className="time">now</div>
    </div>
  );
}
