import React, { useRef, useEffect } from 'react';
import Message from './Message';
import { FiSend, FiPaperclip, FiMic } from 'react-icons/fi';

export default function ChatPanel({
  chat,
  messages,
  isTyping,
  isRecording,
  onSend,
  onImageUpload,
  onVoice,
  onConfirm,
  inputRef,
  fileInputRef
}) {
  const bottomRef = useRef();
  const [inputValue, setInputValue] = React.useState('');

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  const handleSendClick = () => {
    onSend(inputValue);
    setInputValue('');
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSendClick();
    }
  };

  return (
    <div className="chatPanel">
      <div className="chatHeader">
        <div className="cTitle">{chat.name}</div>
        <div className="cStatus">{chat.status}</div>
      </div>

      <div className="messages">
        {messages.map((m, i) => (
          <Message key={i} msg={m} onConfirm={onConfirm} />
        ))}
        {isTyping && (
          <div className="msg bot">
            <div className="bubble">Typing...</div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="composer">
        {/* Hidden file input */}
        <input
          type="file"
          ref={fileInputRef}
          onChange={onImageUpload}
          style={{ display: 'none' }}
          accept="image/*"
        />
        
        <label className="upload" onClick={() => fileInputRef.current.click()}>
          <FiPaperclip />
        </label>
        
        <input
          ref={inputRef}
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyPress}
          placeholder="Type a message"
        />
        
        {isRecording ? (
          <button className="voice rec" onClick={onVoice}>Recording...</button>
        ) : (
          <button className="voice" onClick={onVoice}><FiMic /></button>
        )}

        <button className="send" onClick={handleSendClick}><FiSend /></button>
      </div>
    </div>
  );
}
