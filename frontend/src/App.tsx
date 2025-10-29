import React, { useState, useEffect, useRef } from 'react';
import './App.css';

interface Message {
  id: number;
  text: string;
  isUser: boolean;
  timestamp: Date;
}

interface Status {
  pdf_files: number;
  text_chunks: number;
  ready: boolean;
}

const API_BASE = 'http://localhost:7007';

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<Status | null>(null);
  const [showApiModal, setShowApiModal] = useState(false);
  const [apiKey, setApiKey] = useState('');
  const [generatingKey, setGeneratingKey] = useState(false);
  const [keyGenerated, setKeyGenerated] = useState(false);
  const [processing, setProcessing] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    checkStatus();
    const interval = setInterval(checkStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const checkStatus = async () => {
    try {
      const response = await fetch(`${API_BASE}/status`);
      const data = await response.json();
      setStatus(data);
    } catch (error) {
      console.error('Failed to check status:', error);
    }
  };

  const processPDFs = async () => {
    setProcessing(true);
    try {
      const response = await fetch(`${API_BASE}/process-pdfs`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      const data = await response.json();
      alert(`✅ ${data.message}`);
      checkStatus(); // Refresh status
    } catch (error) {
      alert('❌ Error processing PDFs. Make sure the backend is running.');
    }
    setProcessing(false);
  };

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage: Message = {
      id: Date.now(),
      text: input,
      isUser: true,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch(`${API_BASE}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: input })
      });

      const data = await response.json();

      const botMessage: Message = {
        id: Date.now() + 1,
        text: data.answer,
        isUser: false,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      const errorMessage: Message = {
        id: Date.now() + 1,
        text: 'Sorry, I encountered an error. Please make sure the backend is running.',
        isUser: false,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    }

    setLoading(false);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="app">
      <div className="container">
        <header className="header">
          <h1>📚 MCR Multi RAG</h1>
          <div className="header-controls">
            {status && (
              <div className={`status ${status.ready ? 'ready' : 'not-ready'}`}>
                {status.ready 
                  ? `✅ ${status.pdf_files} PDFs • ${status.text_chunks} chunks`
                  : '❌ No PDFs loaded'
                }
              </div>
            )}
            <button 
              className="process-button"
              onClick={processPDFs}
              disabled={processing}
            >
              {processing ? '⏳ Processing...' : '🔄 Process PDFs'}
            </button>
            <button 
              className="api-button"
              onClick={() => setShowApiModal(true)}
            >
              🔑 Create API Key
            </button>
          </div>
        </header>

        <div className="chat-container">
          <div className="messages">
            {messages.length === 0 && (
              <div className="welcome-message">
                <h3>👋 Welcome to MCR Multi RAG!</h3>
                <p>Ask me about Computer Vision, Multimedia, Haptics, Ethics & more. Multi-course knowledge at your fingertips!</p>
              </div>
            )}
            
            {messages.map((message) => (
              <div key={message.id} className={`message ${message.isUser ? 'user' : 'bot'}`}>
                <div className="message-bubble">
                  {message.text}
                </div>
                <div className="message-time">
                  {message.timestamp.toLocaleTimeString()}
                </div>
              </div>
            ))}
            
            {loading && (
              <div className="message bot">
                <div className="message-bubble loading">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          <div className="input-area">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask a question about your PDFs..."
              disabled={loading}
            />
            <button 
              onClick={sendMessage} 
              disabled={loading || !input.trim()}
              className="send-button"
            >
              {loading ? '⏳' : '📤'}
            </button>
          </div>
        </div>

        {showApiModal && (
          <div className="api-modal" onClick={() => setShowApiModal(false)}>
            <div className="api-modal-content" onClick={(e) => e.stopPropagation()}>
              <h2>🔑 Generate API Key</h2>
              
              {!keyGenerated ? (
                <div className="key-generator">
                  <p>Generate your MCR Multi RAG API key to access the system programmatically.</p>
                  
                  <button 
                    className="generate-key-btn"
                    onClick={async () => {
                      setGeneratingKey(true);
                      try {
                        const response = await fetch(`${API_BASE}/create-api-key`, {
                          method: 'POST',
                          headers: { 'Content-Type': 'application/json' }
                        });
                        const data = await response.json();
                        setApiKey(data.api_key);
                        setKeyGenerated(true);
                      } catch (error) {
                        alert('Error generating API key. Make sure the backend is running.');
                      }
                      setGeneratingKey(false);
                    }}
                    disabled={generatingKey}
                  >
                    {generatingKey ? '⏳ Generating...' : '🔑 Generate API Key'}
                  </button>
                </div>
              ) : (
                <div className="key-display">
                  <h3>✅ API Key Generated!</h3>
                  <div className="key-box">
                    <code id="api-key-text">{apiKey}</code>
                    <button 
                      className="copy-btn"
                      onClick={async () => {
                        try {
                          const keyText = apiKey?.trim();
                          if (!keyText) {
                            alert('❌ No API key to copy');
                            return;
                          }
                          
                          if (navigator.clipboard) {
                            await navigator.clipboard.writeText(keyText);
                            alert('✅ API Key copied to clipboard!');
                          } else {
                            // Fallback method
                            const textArea = document.createElement('textarea');
                            textArea.value = keyText;
                            textArea.style.position = 'fixed';
                            textArea.style.left = '-999999px';
                            textArea.style.top = '-999999px';
                            document.body.appendChild(textArea);
                            textArea.focus();
                            textArea.select();
                            const successful = document.execCommand('copy');
                            document.body.removeChild(textArea);
                            
                            if (successful) {
                              alert('✅ API Key copied to clipboard!');
                            } else {
                              alert('❌ Copy failed. Please select and copy manually.');
                            }
                          }
                        } catch (err) {
                          console.error('Copy failed:', err);
                          alert('❌ Copy failed. Please select the key and copy manually (Ctrl+C).');
                        }
                      }}
                    >
                      📋 Copy
                    </button>
                  </div>
                  
                  <div className="usage-info">
                    <h4>How to use:</h4>
                    <div className="code-example">
                      <code>
{`curl -X POST "http://localhost:8000/query" \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer ${apiKey}" \\
  -d '{"question": "What is computer vision?"}'`}
                      </code>
                    </div>
                  </div>
                </div>
              )}
              
              <button className="close-modal" onClick={() => {
                setShowApiModal(false);
                setApiKey('');
                setKeyGenerated(false);
              }}>
                Close 👍
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;