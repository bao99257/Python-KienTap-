import React from 'react';
import ChatBot from '../components/ChatBot';

const ChatBotPage = () => {
  return (
    <div>
      <div className="container-fluid py-3">
        <div className="row">
          <div className="col-12">
            <div className="d-flex justify-content-between align-items-center mb-3">
              <h2>AI Chatbot</h2>
              <div className="text-muted">
                <small>Powered by Ollama</small>
              </div>
            </div>
          </div>
        </div>
      </div>
      <ChatBot />
    </div>
  );
};

export default ChatBotPage;
