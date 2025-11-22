import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { message } from 'antd';
import { PaperClipOutlined, LogoutOutlined, AudioOutlined, SendOutlined } from '@ant-design/icons';
import SummaryCard from './SummaryCard';
import './Chat.css';

function Chat({ handleLogout }) {
  const [messages, setMessages] = useState([
    { type: 'text', text: 'Hello! How can I help you today?', sender: 'bot' },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [menuVisible, setMenuVisible] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const token = localStorage.getItem('token');
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const menuOptions = [
    '📸 Upload Bill',
    '🎤 Voice Expense',
    '📊 Monthly Summary',
    '🧾 GST Inputs',
    '❓ Help',
  ];

  const handleSendMessage = async (text) => {
    if (text.trim()) {
      const userMessage = { type: 'text', text, sender: 'user' };
      setMessages((prevMessages) => [...prevMessages, userMessage]);
      setInputValue('');
      
      if (text === '📊 Monthly Summary') {
        setIsTyping(true);
        setTimeout(() => {
          const summaryData = {
            title: 'Monthly Summary for November 2025',
            totalSpend: '₹12,540.00',
            topVendors: ['Zomato', 'Swiggy', 'Indian Oil'],
            gstInput: '₹1,881.00',
            categoryBreakdown: {
              '🍔 Food': '₹4,500.00',
              '⛽ Fuel': '₹3,000.00',
              '🛍️ Shopping': '₹5,040.00',
            },
          };
          const botMessage = { type: 'summary_card', data: summaryData, sender: 'bot' };
          setMessages((prevMessages) => [...prevMessages, botMessage]);
          setIsTyping(false);
        }, 1000);
        return;
      }

      setIsTyping(true);
      try {
        const response = await axios.post(
          '/webhook/text',
          { text },
          { headers: { Authorization: `Bearer ${token}` } }
        );
        const botMessage = { type: 'text', text: response.data.text, sender: 'bot' };
        setMessages((prevMessages) => [...prevMessages, botMessage]);
      } catch (error) {
        console.error("Failed to send message:", error);
        if (error.response) {
          if (error.response.status === 401) {
            message.error('Authentication failed. Please log in again.');
          } else if (error.response.status === 503) {
            message.error('A required service is unavailable. Please try again later.');
          } else {
            message.error(`Server error: ${error.response.status}. Please try again.`);
          }
        } else if (error.request) {
          message.error('Network error. Could not connect to the server.');
        } else {
          message.error('An unexpected error occurred. Please try again.');
        }
      } finally {
        setIsTyping(false);
      }
    }
  };

  const handleInputChange = (e) => {
    setInputValue(e.target.value);
    if (e.target.value.trim() !== '') {
      setMenuVisible(false);
    }
  };
  
  const handleMenuOptionClick = (option) => {
    if (option === '📸 Upload Bill') {
      fileInputRef.current.click();
    } else if (option === '🎤 Voice Expense') {
        handleSendMessage(option)
    } 
    else {
      handleSendMessage(option);
    }
    setMenuVisible(false);
  };

  const handleImageUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      const imageMessage = {
        type: 'image',
        src: e.target.result,
        sender: 'user',
      };
      setMessages((prevMessages) => [...prevMessages, imageMessage]);
    };
    reader.readAsDataURL(file);

    setIsTyping(true);
    const formData = new FormData();
    formData.append('image', file);

    try {
      const response = await axios.post('/webhook/image', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          Authorization: `Bearer ${token}`,
        },
      });
      
      const confirmationMessage = {
          type: 'confirmation',
          data: response.data,
          sender: 'bot'
      };
      setMessages((prevMessages) => [...prevMessages, confirmationMessage]);

    } catch (error) {
      console.error("Failed to process image:", error);
      if (error.response) {
        if (error.response.status === 401) {
          message.error('Authentication failed. Please log in again.');
        } else if (error.response.status === 503) {
          message.error('An image processing service is unavailable. Please try again later.');
        } else {
          message.error(`Server error: ${error.response.status}. Failed to process image.`);
        }
      } else if (error.request) {
        message.error('Network error. Could not connect to the server.');
      } else {
        message.error('An unexpected error occurred while uploading the image.');
      }
    } finally {
      setIsTyping(false);
      // Reset file input
      event.target.value = null;
    }
  };

  const handleConfirmation = (action) => {
    setMessages(messages.filter(m => m.type !== 'confirmation'));

    const responseText = action === 'confirm' ? '✅ Expense confirmed and recorded.' : '❌ Action cancelled.';
    const botMessage = { type: 'text', text: responseText, sender: 'bot' };
    setMessages((prevMessages) => [...prevMessages, botMessage]);
  };

  const renderMessage = (msg, index) => {
    switch (msg.type) {
      case 'summary_card':
        return (
          <div key={index} className={`message ${msg.sender}`}>
            <SummaryCard data={msg.data} />
          </div>
        );
      case 'image':
        return (
          <div key={index} className={`message ${msg.sender}`}>
            <img src={msg.src} alt="Uploaded bill" className="message-image" />
          </div>
        );
      case 'confirmation':
        return (
            <div key={index} className={`message ${msg.sender}`}>
                <div className="confirmation-card">
                    <div className="confirmation-header">Extracted Data</div>
                    <div className="confirmation-body">
                        {Object.entries(msg.data).map(([key, value]) => (
                            <div key={key} className="confirmation-item">
                                <span className="confirmation-label">{key}:</span>
                                <span className="confirmation-value">{value}</span>
                            </div>
                        ))}
                    </div>
                    <div className="confirmation-buttons">
                        <button onClick={() => handleConfirmation('confirm')}>Confirm</button>
                        <button onClick={() => handleConfirmation('retry')}>Retry</button>
                    </div>
                </div>
            </div>
        );
      default:
        return (
          <div key={index} className={`message ${msg.sender}`}>
            {msg.text}
          </div>
        );
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h3>Vyapar Bot</h3>
        <button onClick={handleLogout} className="logout-button">
          <LogoutOutlined />
        </button>
      </div>
      <div className="chat-messages">
        {messages.map((msg, index) => renderMessage(msg, index))}
        {isTyping && (
          <div className="message bot typing-indicator">
            <span></span><span></span><span></span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleImageUpload}
        style={{ display: 'none' }}
        accept="image/*"
      />
      {menuVisible && (
        <div className="menu-panel">
          {menuOptions.map((option, index) => (
            <div key={index} className="menu-option" onClick={() => handleMenuOptionClick(option)}>
              {option}
            </div>
          ))}
        </div>
      )}
      <div className="chat-input">
        <button className="menu-button" onClick={() => setMenuVisible(!menuVisible)}>
          <PaperClipOutlined />
        </button>
          <div className="chat-input-buttons">
            {isRecording ? (
                <button onClick={handleVoiceExpenseClick} className="voice-button recording">
                    <span className="recording-dot"></span> Stop
                </button>
            ) : (
            <>
                <input
                  type="text"
                  value={inputValue}
                  onChange={handleInputChange}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter' && inputValue.trim()) {
                        handleSendMessage(inputValue);
                    }
                  }}
                  placeholder="Type a message..."
                />
                {inputValue ? (
                  <button className="send-button" onClick={() => {
                      if (inputValue.trim()) {
                          handleSendMessage(inputValue);
                      }
                  }}>
                      <SendOutlined />
                  </button>
                ) : (
                  <button onClick={handleVoiceExpenseClick} className="voice-button">
                      <AudioOutlined />
                  </button>
                )}
            </>
            )}
          </div>
        </div>
    </div>
  );
}

export default Chat;
