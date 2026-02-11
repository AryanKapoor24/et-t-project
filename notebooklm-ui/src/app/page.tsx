
'use client';

import { useState, useEffect } from 'react';
import SpaceScene from '@/components/SpaceScene';
import ChatInterface from '@/components/ChatInterface';
import DocumentUpload from '@/components/DocumentUpload';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: any[];
  timestamp: Date;
}

interface Document {
  id: string;
  name: string;
  type: string;
  size: number;
  chunks: number;
  uploaded_at: string;
}

export default function Home() {
  const [isOpen, setIsOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<'chat' | 'upload'>('chat');
  const [documents, setDocuments] = useState<Document[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      const response = await fetch(`${API_URL}/documents`);
      const data = await response.json();
      setDocuments(data.documents || []);
    } catch (error) {
      console.error('Error fetching documents:', error);
    }
  };

  const handleBlackHoleClick = () => {
    setIsOpen(true);
  };

  const handleClose = () => {
    setIsOpen(false);
  };

  const handleFileUpload = async (files: FileList) => {
    setIsLoading(true);
    const formData = new FormData();
    
    Array.from(files).forEach(file => {
      formData.append('files', file);
    });

    try {
      const response = await fetch(`${API_URL}/upload`, {
        method: 'POST',
        body: formData,
      });
      
      const data = await response.json();
      
      if (data.success) {
        await fetchDocuments();
      }
    } catch (error) {
      console.error('Error uploading files:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async (message: string) => {
    const userMessage: Message = { 
      role: 'user', 
      content: message, 
      timestamp: new Date() 
    };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await fetch(`${API_URL}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: message }),
      });

      const data = await response.json();
      
      const assistantMessage: Message = {
        role: 'assistant',
        content: data.response,
        sources: data.sources,
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Sorry, there was an error processing your request.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="cosmic-app">
      <SpaceScene onBlackHoleClick={handleBlackHoleClick} isOpen={isOpen} />
      
      {!isOpen && (
        <div className="cosmic-hint">
          <div className="hint-content">
            <span className="hint-icon">👆</span>
            <p>Click the black hole to enter the knowledge portal</p>
          </div>
        </div>
      )}

      <div className={`cosmic-portal ${isOpen ? 'open' : ''}`}>
        <div className="portal-container">
          <button className="close-portal" onClick={handleClose}>
            <span>×</span>
          </button>

          <div className="portal-tabs">
            <button 
              className={`portal-tab ${activeTab === 'chat' ? 'active' : ''}`}
              onClick={() => setActiveTab('chat')}
            >
              <span className="tab-icon">💬</span>
              Chat
            </button>
            <button 
              className={`portal-tab ${activeTab === 'upload' ? 'active' : ''}`}
              onClick={() => setActiveTab('upload')}
            >
              <span className="tab-icon">📚</span>
              Upload ({documents.length})
            </button>
          </div>

          <div className="portal-content">
            {activeTab === 'chat' ? (
              <ChatInterface 
                messages={messages}
                onSendMessage={handleSendMessage}
                isLoading={isLoading}
              />
            ) : (
              <DocumentUpload 
                documents={documents}
                onFileUpload={handleFileUpload}
                isLoading={isLoading}
              />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
