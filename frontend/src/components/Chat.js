import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';
import './Chat.css';

const QUICK_ACTIONS = [
  '📸 Upload Bill',
  '📊 Monthly Summary',
  '🧾 GST Help',
  '📋 Dashboard',
];

export default function Chat({ handleLogout }) {
  const [messages, setMessages] = useState([
    { type: 'text', text: 'Welcome to Vyapar AI! 🙏\n\nI can help you:\n• Record expenses (type or upload bills)\n• Create invoices\n• Answer GST questions\n• Show summaries\n\nTry saying: "Paid ₹500 to Sharma Store for groceries"', sender: 'bot', time: new Date() },
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [recognition, setRecognition] = useState(null);
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);
  const navigate = useNavigate();

  // Scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  // Initialize Web Speech API for voice (free, client-side)
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const rec = new SpeechRecognition();
      rec.continuous = false;
      rec.interimResults = false;
      rec.lang = 'hi-IN'; // Hindi + English
      rec.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setInput(transcript);
        setIsRecording(false);
        // Auto-send after speech recognition
        handleSendText(transcript);
      };
      rec.onerror = () => setIsRecording(false);
      rec.onend = () => setIsRecording(false);
      setRecognition(rec);
    }
  }, []); // eslint-disable-line

  const addMessage = (msg) => setMessages(prev => [...prev, { ...msg, time: new Date() }]);

  const handleSendText = async (text) => {
    if (!text?.trim()) return;
    const trimmed = text.trim();
    setInput('');

    // Handle special quick actions
    if (trimmed === '📋 Dashboard') {
      navigate('/dashboard');
      return;
    }
    if (trimmed === '📸 Upload Bill') {
      fileInputRef.current?.click();
      return;
    }

    addMessage({ type: 'text', text: trimmed, sender: 'user' });
    setIsTyping(true);

    try {
      const response = await api.post('/api/webhook/text', { text: trimmed });
      const data = response.data;

      if (data.data && (data.data.by_category || data.data.expense_count !== undefined)) {
        addMessage({ type: 'summary', data: data.data, text: data.message, sender: 'bot' });
      } else if (data.data?.needs_confirmation) {
        addMessage({ type: 'confirmation', data: data.data, text: data.message, sender: 'bot' });
      } else {
        addMessage({ type: 'text', text: data.message, sender: 'bot' });
      }
    } catch (err) {
      const errMsg = err.response?.status === 503
        ? '⚠️ AI service temporarily unavailable. Please try again.'
        : '❌ Something went wrong. Please try again.';
      addMessage({ type: 'text', text: errMsg, sender: 'bot' });
    } finally {
      setIsTyping(false);
    }
  };

  const handleImageUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Show preview
    const reader = new FileReader();
    reader.onload = (ev) => addMessage({ type: 'image', src: ev.target.result, sender: 'user' });
    reader.readAsDataURL(file);

    setIsTyping(true);
    try {
      const formData = new FormData();
      formData.append('image', file);
      const response = await api.post('/api/webhook/image', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      addMessage({ type: 'confirmation', data: response.data.data, text: response.data.message, sender: 'bot' });
    } catch (err) {
      addMessage({ type: 'text', text: '❌ Failed to process image. Please try again.', sender: 'bot' });
    } finally {
      setIsTyping(false);
      e.target.value = null;
    }
  };

  const handleConfirm = async (expenseData) => {
    setIsTyping(true);
    try {
      const response = await api.post('/api/webhook/image/confirm', expenseData);
      addMessage({ type: 'text', text: response.data.message, sender: 'bot' });
    } catch {
      addMessage({ type: 'text', text: '❌ Failed to save expense.', sender: 'bot' });
    } finally {
      setIsTyping(false);
    }
  };

  const toggleRecording = () => {
    if (!recognition) {
      addMessage({ type: 'text', text: '⚠️ Voice input is not supported in this browser. Please use Chrome.', sender: 'bot' });
      return;
    }
    if (isRecording) {
      recognition.stop();
    } else {
      recognition.start();
      setIsRecording(true);
    }
  };

  const formatTime = (d) => {
    if (!d) return '';
    return new Date(d).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });
  };

  const renderMessage = (msg, i) => {
    const timeStr = formatTime(msg.time);
    switch (msg.type) {
      case 'image':
        return (
          <div key={i} className={`message ${msg.sender}`}>
            <div className="msg-image"><img src={msg.src} alt="Uploaded" /></div>
            <div className="msg-time">{timeStr}</div>
          </div>
        );
      case 'confirmation':
        const preview = msg.data?.expense_preview || msg.data?.extracted || {};
        return (
          <div key={i} className={`message ${msg.sender}`}>
            <div className="confirm-card">
              <div className="confirm-card-header">📸 Extracted Data</div>
              <div className="confirm-card-body">
                {Object.entries(preview).filter(([k]) => !['source','gst_applicable','notes','currency'].includes(k)).map(([k, v]) => (
                  <div key={k} className="confirm-row">
                    <span className="label">{k.replace(/_/g, ' ')}</span>
                    <span className="value">{typeof v === 'number' ? `₹${v.toLocaleString()}` : String(v)}</span>
                  </div>
                ))}
              </div>
              <div className="confirm-card-actions">
                <button onClick={() => handleConfirm(msg.data.expense_preview)}>✅ Confirm</button>
                <button onClick={() => addMessage({ type: 'text', text: 'Cancelled.', sender: 'bot' })}>❌ Cancel</button>
              </div>
            </div>
            <div className="msg-time">{timeStr}</div>
          </div>
        );
      case 'summary':
        const s = msg.data || {};
        return (
          <div key={i} className={`message ${msg.sender}`}>
            <div className="summary-card">
              <div className="summary-card-header">📊 {s.period || 'Summary'}</div>
              <div className="summary-card-body">
                <div className="summary-stat"><span className="label">Total Spent</span><span className="value highlight">₹{(s.total_amount || 0).toLocaleString()}</span></div>
                <div className="summary-stat"><span className="label">Expenses</span><span className="value">{s.expense_count || 0}</span></div>
                <div className="summary-stat"><span className="label">GST Input</span><span className="value">₹{(s.gst_total || 0).toLocaleString()}</span></div>
                {s.top_vendors?.length > 0 && (
                  <div className="summary-stat"><span className="label">Top Vendors</span><span className="value">{s.top_vendors.join(', ')}</span></div>
                )}
                {s.by_category && Object.keys(s.by_category).length > 0 && (
                  <>
                    <hr style={{ border: 'none', borderTop: '1px solid var(--border)', margin: '4px 0' }} />
                    {Object.entries(s.by_category).map(([cat, amt]) => (
                      <div key={cat} className="summary-stat">
                        <span className="label">{cat}</span>
                        <span className="value">₹{amt.toLocaleString()}</span>
                      </div>
                    ))}
                  </>
                )}
              </div>
            </div>
            <div className="msg-time">{timeStr}</div>
          </div>
        );
      default:
        return (
          <div key={i} className={`message ${msg.sender}`}>
            <div className="msg-bubble">{msg.text}</div>
            <div className="msg-time">{timeStr}</div>
          </div>
        );
    }
  };

  return (
    <div className="chat-page">
      <div className="chat-header">
        <div className="chat-header-left">
          <div className="chat-avatar">V</div>
          <div className="chat-header-info">
            <h3>Vyapar AI</h3>
            <span>● Online</span>
          </div>
        </div>
        <div className="chat-header-actions">
          <button className="header-btn" onClick={() => navigate('/dashboard')}>📊 <span>Dashboard</span></button>
          <button className="header-btn danger" onClick={handleLogout}>↪ <span>Logout</span></button>
        </div>
      </div>

      <div className="chat-messages">
        {messages.map(renderMessage)}
        {isTyping && <div className="typing"><span></span><span></span><span></span></div>}
        <div ref={messagesEndRef} />
      </div>

      <div className="quick-menu">
        {QUICK_ACTIONS.map(action => (
          <button key={action} className="quick-btn" onClick={() => handleSendText(action)}>{action}</button>
        ))}
      </div>

      <input type="file" ref={fileInputRef} onChange={handleImageUpload} style={{ display: 'none' }} accept="image/*" />

      <div className="chat-composer">
        <button className="composer-btn attach" onClick={() => fileInputRef.current?.click()}>📎</button>
        <input
          className="composer-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSendText(input)}
          placeholder={isRecording ? '🎤 Listening...' : 'Type a message...'}
          disabled={isRecording}
        />
        {input ? (
          <button className="composer-btn send" onClick={() => handleSendText(input)}>➤</button>
        ) : (
          <button className={`composer-btn mic ${isRecording ? 'recording' : ''}`} onClick={toggleRecording}>
            {isRecording ? '⏹' : '🎤'}
          </button>
        )}
      </div>
    </div>
  );
}
