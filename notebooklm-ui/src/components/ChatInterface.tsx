'use client';

import { useState, useRef, useEffect } from 'react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: Array<{
    document: string;
    score: number;
    chunk_index: number;
  }>;
  timestamp: Date;
}

interface ChatInterfaceProps {
  messages: Message[];
  onSendMessage: (message: string) => void;
  isLoading: boolean;
}

export default function ChatInterface({ messages, onSendMessage, isLoading }: ChatInterfaceProps) {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      onSendMessage(input.trim());
      setInput('');
    }
  };

  return (
    <div className="chat-interface-cosmic">
      <div className="cosmic-header">
        <div className="cosmic-title">
          <span className="cosmic-icon">🌌</span>
          <h2>Cosmic Knowledge Assistant</h2>
        </div>
        <p className="cosmic-subtitle">Ask anything about your uploaded documents</p>
      </div>

      <div className="chat-messages-cosmic">
        {messages.length === 0 ? (
          <div className="chat-empty-cosmic">
            <div className="empty-icon-cosmic">✨</div>
            <h3>Ready to explore your knowledge universe</h3>
            <p>Upload documents and ask questions to unlock insights</p>
            <div className="suggested-queries-cosmic">
              <button 
                className="suggested-query-cosmic"
                onClick={() => setInput('Summarize the key points from my documents')}
              >
                📝 Summarize documents
              </button>
              <button 
                className="suggested-query-cosmic"
                onClick={() => setInput('What are the main insights?')}
              >
                💡 Find insights
              </button>
              <button 
                className="suggested-query-cosmic"
                onClick={() => setInput('Explain the core concepts')}
              >
                🎯 Explain concepts
              </button>
            </div>
          </div>
        ) : (
          <>
            {messages.map((message, index) => (
              <div 
                key={index} 
                className={`message-cosmic ${message.role}`}
              >
                <div className="message-avatar-cosmic">
                  {message.role === 'user' ? '👤' : '🤖'}
                </div>
                <div className="message-content-cosmic">
                  <div className="message-text-cosmic">
                    {message.content}
                  </div>
                  {message.sources && message.sources.length > 0 && (
                    <div className="message-sources-cosmic">
                      <div className="sources-header-cosmic">📚 Sources:</div>
                      {message.sources.map((source, idx) => (
                        <div key={idx} className="source-item-cosmic">
                          <span className="source-doc-cosmic">{source.document}</span>
                          <span className="source-score-cosmic">
                            {(source.score * 100).toFixed(0)}% relevant
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                  <div className="message-timestamp-cosmic">
                    {new Date(message.timestamp).toLocaleTimeString()}
                  </div>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="message-cosmic assistant">
                <div className="message-avatar-cosmic">🤖</div>
                <div className="message-content-cosmic">
                  <div className="typing-indicator-cosmic">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      <form className="chat-input-form-cosmic" onSubmit={handleSubmit}>
        <div className="input-container-cosmic">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e);
              }
            }}
            placeholder="Ask the cosmos anything..."
            className="chat-input-cosmic"
            rows={1}
            disabled={isLoading}
          />
          <button 
            type="submit" 
            className="send-button-cosmic"
            disabled={!input.trim() || isLoading}
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z" />
            </svg>
          </button>
        </div>
      </form>
    </div>
  );
}
