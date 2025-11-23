import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import LeftSidebar from './components/LeftSidebar';
import ChatPanel from './components/ChatPanel';
import Login from './components/Login';

// Main App component
export default function App() {
  const [token, setToken] = useState(localStorage.getItem('token'));

  const handleLoginSuccess = (newToken) => {
    localStorage.setItem('token', newToken);
    setToken(newToken);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken(null);
  };

  if (!token) {
    return <Login onLoginSuccess={handleLoginSuccess} />;
  }

  return <ChatApp token={token} handleLogout={handleLogout} />;
}


// The main chat application, rendered only when authenticated
function ChatApp({ token, handleLogout }) {
  // State Management
  const [messages, setMessages] = useState([
    { from: 'bot', text: 'Welcome to VyaparAI — your WhatsApp AI accountant. Type a message or use the menu to begin.' }
  ]);
  const [activeChat, setActiveChat] = useState({ name: 'VyaparAI', status: 'online' });
  const [isTyping, setIsTyping] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  
  // Refs
  const inputRef = useRef();
  const fileInputRef = useRef(null);
  const mediaRecorder = useRef(null);

  // Effect to scroll to the bottom of the messages
  useEffect(() => {
    window.scrollTo(0, document.body.scrollHeight);
  }, [messages, isTyping]);

  // Push a new message to the state
  const pushMessage = (msg) => {
    setMessages(prev => [...prev, msg]);
  };

  // Handle Text Message Submission
  const handleSendMessage = async (text) => {
    if (!text || text.trim() === '') return;
    
    pushMessage({ from: 'user', text });
    if(inputRef.current) inputRef.current.value = '';

    setIsTyping(true);

    // Monthly Summary Client-Side Trigger
    if (text.toLowerCase().trim() === 'monthly summary') {
      try {
        const response = await axios.get('/summary/monthly', {
          headers: { Authorization: `Bearer ${token}` },
        });
        pushMessage({ type: 'summary_card', from: 'bot', data: response.data });
      } catch (error) {
        console.error("Failed to fetch summary:", error);
        pushMessage({ from: 'bot', text: 'Sorry, I failed to fetch the monthly summary.' });
      } finally {
        setIsTyping(false);
      }
      return;
    }

    // Default text processing via backend
    try {
      const response = await axios.post('/webhook/text', { text }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      pushMessage({ from: 'bot', text: response.data.text });
    } catch (error)      {
        console.error("Failed to send message:", error);
        let errorText = 'An unexpected error occurred.';
        if (error.response) {
            if (error.response.status === 401) {
              errorText = 'Authentication failed. Please log in again.';
              handleLogout(); // Log out on auth failure
            }
            else if (error.response.status === 503) errorText = 'A required service is unavailable. Please try again later.';
            else errorText = `Server error: ${error.response.status}. Please try again.`;
        } else if (error.request) {
            errorText = 'Network error. Could not connect to the server.';
        }
        pushMessage({ from: 'bot', text: errorText });
    } finally {
      setIsTyping(false);
    }
  };

  // Handle Image Upload
  const handleImageUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    pushMessage({ type: 'image', from: 'user', src: URL.createObjectURL(file) });

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
      pushMessage({ type: 'confirmation', from: 'bot', data: response.data });
    } catch (error) {
      console.error("Failed to process image:", error);
      pushMessage({ from: 'bot', text: 'Sorry, I failed to process the image.' });
    } finally {
      setIsTyping(false);
      event.target.value = null; // Reset file input
    }
  };

  // Handle Confirmation of OCR
  const handleConfirmation = async (action, data) => {
    setMessages(prev => prev.filter(m => m.type !== 'confirmation'));

    if (action === 'confirm') {
      setIsTyping(true);
      try {
        const expenseData = {
          item: data.Vendor,
          amount: parseFloat(data['Total Amount']),
          date: data.Date ? new Date(data.Date).toISOString().split('T')[0] : new Date().toISOString().split('T')[0],
        };
        await axios.post('/expenses/confirm_ocr', expenseData, {
          headers: { Authorization: `Bearer ${token}` },
        });
        pushMessage({ from: 'bot', text: '✅ Expense confirmed and recorded.' });
      } catch (error) {
        console.error("Failed to confirm expense:", error);
        pushMessage({ from: 'bot', text: '❌ Failed to record expense.' });
      } finally {
        setIsTyping(false);
      }
    } else {
      pushMessage({ from: 'bot', text: '❌ Action cancelled.' });
    }
  };

  // Handle Voice Recording
  const handleVoiceRecording = async () => {
    if (isRecording) {
      mediaRecorder.current.stop();
      setIsRecording(false);
    } else {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder.current = new MediaRecorder(stream);
        const audioChunks = [];

        mediaRecorder.current.ondataavailable = (event) => audioChunks.push(event.data);

        mediaRecorder.current.onstop = async () => {
          const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
          const formData = new FormData();
          formData.append('from_number', 'frontend');
          formData.append('audio', audioBlob, 'voice_expense.webm');

          setIsTyping(true);
          try {
            const response = await axios.post('/webhook/audio', formData, {
              headers: { Authorization: `Bearer ${token}` },
            });
            pushMessage({ from: 'bot', text: response.data.summary });
          } catch (error) {
            console.error("Failed to send voice expense:", error);
            pushMessage({ from: 'bot', text: 'Failed to process voice expense.' });
          } finally {
            setIsTyping(false);
          }
        };
        mediaRecorder.current.start();
        setIsRecording(true);
      } catch (error) {
        console.error("Failed to start recording:", error);
        pushMessage({ from: 'bot', text: 'Could not start recording. Please ensure microphone permissions.' });
      }
    }
  };

  return (
    <div className="app">
      <LeftSidebar active={activeChat} onSelect={setActiveChat} onLogout={handleLogout} />
      <ChatPanel
        chat={activeChat}
        messages={messages}
        isTyping={isTyping}
        isRecording={isRecording}
        onSend={handleSendMessage}
        onImageUpload={handleImageUpload}
        onVoice={handleVoiceRecording}
        onConfirm={handleConfirmation}
        inputRef={inputRef}
        fileInputRef={fileInputRef}
      />
    </div>
  );
}
