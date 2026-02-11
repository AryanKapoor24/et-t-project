'use client';

import { useState, useRef } from 'react';

interface Document {
  id: string;
  name: string;
  type: string;
  size: number;
  chunks: number;
  uploaded_at: string;
}

interface DocumentUploadProps {
  documents: Document[];
  onFileUpload: (files: FileList) => void;
  isLoading: boolean;
}

export default function DocumentUpload({ documents, onFileUpload, isLoading }: DocumentUploadProps) {
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      onFileUpload(e.dataTransfer.files);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      onFileUpload(e.target.files);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  };

  return (
    <div className="document-upload-cosmic">
      <div className="cosmic-header">
        <div className="cosmic-title">
          <span className="cosmic-icon">📚</span>
          <h2>Knowledge Universe</h2>
        </div>
        <p className="cosmic-subtitle">Upload documents to expand your cosmic knowledge base</p>
      </div>

      <div className="upload-section-cosmic">
        <div
          className={`drop-zone-cosmic ${dragActive ? 'active' : ''} ${isLoading ? 'loading' : ''}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => !isLoading && fileInputRef.current?.click()}
        >
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept=".pdf,.txt,.docx,.md"
            onChange={handleFileChange}
            style={{ display: 'none' }}
            disabled={isLoading}
          />
          
          {isLoading ? (
            <div className="upload-loading-cosmic">
              <div className="cosmic-spinner"></div>
              <p>Processing through the cosmos...</p>
            </div>
          ) : (
            <>
              <div className="upload-icon-cosmic">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                  <polyline points="17 8 12 3 7 8" />
                  <line x1="12" y1="3" x2="12" y2="15" />
                </svg>
              </div>
              <p className="upload-text-cosmic">
                <strong>Click to upload</strong> or drag files into the cosmos
              </p>
              <p className="upload-hint-cosmic">
                PDF, TXT, DOCX, MD • Up to 10MB each
              </p>
            </>
          )}
        </div>
      </div>

      {documents.length > 0 && (
        <div className="documents-section-cosmic">
          <h3 className="section-subtitle-cosmic">Your Cosmic Library ({documents.length})</h3>
          
          <div className="documents-grid-cosmic">
            {documents.map((doc) => (
              <div key={doc.id} className="document-card-cosmic">
                <div className="doc-icon-cosmic">
                  {doc.type === 'pdf' && '📄'}
                  {doc.type === 'txt' && '📝'}
                  {doc.type === 'docx' && '📘'}
                  {doc.type === 'md' && '📋'}
                </div>
                <div className="doc-info-cosmic">
                  <h4 className="doc-name-cosmic">{doc.name}</h4>
                  <div className="doc-meta-cosmic">
                    <span>{formatFileSize(doc.size)}</span>
                    <span className="doc-separator">•</span>
                    <span>{doc.chunks} chunks</span>
                  </div>
                  <div className="doc-date-cosmic">
                    {formatDate(doc.uploaded_at)}
                  </div>
                </div>
                <div className="doc-status-cosmic">
                  <span className="status-badge-cosmic">✓ Indexed</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
