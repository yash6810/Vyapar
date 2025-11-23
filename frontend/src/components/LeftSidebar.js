import React from 'react';
import { FiSearch, FiLogOut } from 'react-icons/fi';

export default function LeftSidebar({ active, onSelect, onLogout }) {
  const buttonStyle = {
    background: 'none',
    border: 'none',
    color: '#555',
    cursor: 'pointer',
    fontSize: '1.2rem',
    marginLeft: 'auto'
  };

  // This is a simplified version for the single-chat view.
  return (
    <div className="left">
      <div className="profile">
        <div className="avatar">Y</div>
        <div>
          <div className="name">You</div>
          <div className="status">Online</div>
        </div>
        <button onClick={onLogout} style={buttonStyle} title="Logout">
          <FiLogOut />
        </button>
      </div>
      <div className="search"><FiSearch /> <input placeholder="Search or start new chat" /></div>
      <div className="chats">
        <div className={"chatItem " + (active.name === 'VyaparAI' ? 'active' : '')} onClick={() => onSelect({ name: 'VyaparAI', status: 'online' })}>
          <div className="cAvatar">V</div>
          <div className="cInfo">
            <div className="cName">VyaparAI</div>
            <div className="cLast">Online</div>
          </div>
        </div>
      </div>
    </div>
  );
}
