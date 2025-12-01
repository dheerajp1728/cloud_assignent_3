import React, { useState } from 'react';
import './App.css';
import SearchSection from './components/SearchSection';
import UploadSection from './components/UploadSection';
import Message from './components/Message';

function App() {
  const [message, setMessage] = useState({ text: '', type: '' });

  const showMessage = (text, type) => {
    setMessage({ text, type });
    setTimeout(() => {
      setMessage({ text: '', type: '' });
    }, 5000);
  };

  return (
    <div className="container">
      <h1>📷 AI Photo Search</h1>
      <p className="subtitle">
        Search your photos using natural language powered by AWS Lex & Rekognition
      </p>

      <Message message={message.text} type={message.type} />

      <SearchSection showMessage={showMessage} />
      <UploadSection showMessage={showMessage} />

      <div className="footer">
        <p>Powered by AWS Lambda, Lex, Rekognition, OpenSearch & API Gateway</p>
      </div>
    </div>
  );
}

export default App;
