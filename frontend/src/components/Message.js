import React from 'react';

function Message({ message, type }) {
  if (!message) return null;

  return (
    <div className={`message ${type}`}>
      {message}
    </div>
  );
}

export default Message;
