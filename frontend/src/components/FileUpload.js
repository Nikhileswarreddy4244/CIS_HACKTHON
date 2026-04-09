import React, { useState, useRef } from 'react';
import { uploadFile } from '../services/api';
import { formatFileSize } from '../utils/helpers';
import './FileUpload.css';

function FileUpload({ onUploadSuccess }) {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState(null);
  const inputRef = useRef(null);

  const handleDrop = (e) => {
    e.preventDefault();
    setDragActive(false);
    const file = e.dataTransfer.files[0];
    if (file) setSelectedFile(file);
  };

  const handleChange = (e) => {
    const file = e.target.files[0];
    if (file) setSelectedFile(file);
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    setUploading(true);
    setProgress(0);
    setMessage(null);

    try {
      // Simulate progress
      const interval = setInterval(() => {
        setProgress(p => (p < 85 ? p + 10 : p));
      }, 200);

      await uploadFile(selectedFile);

      clearInterval(interval);
      setProgress(100);
      setMessage({ type: 'success', text: `"${selectedFile.name}" was uploaded successfully!` });
      setSelectedFile(null);
      if (onUploadSuccess) onUploadSuccess();
    } catch (err) {
      // err.message already contains the friendly text set by the axios interceptor
      const isDuplicate = err.status === 409;
      const isHarmful   = err.status === 422;
      setMessage({
        type: isHarmful ? 'danger' : 'error',
        icon: isHarmful ? '🛡️' : '⚠',
        text: err.message,
        hint: isHarmful
          ? 'Only safe documents, images, and media files are accepted.'
          : isDuplicate
          ? 'Tip: Open the History page to see existing files and their versions.'
          : null,
      });
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="file-upload" id="file-upload-section">
      {/* Drop Zone */}
      <div
        className={`drop-zone ${dragActive ? 'active' : ''} ${selectedFile ? 'has-file' : ''}`}
        onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
        onDragLeave={() => setDragActive(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        role="button"
        tabIndex={0}
        aria-label="File upload drop zone"
        id="drop-zone"
      >
        <input
          ref={inputRef}
          type="file"
          id="file-input"
          className="hidden-input"
          onChange={handleChange}
        />
        {selectedFile ? (
          <div className="file-preview">
            <span className="file-preview-icon">📄</span>
            <div className="file-preview-info">
              <p className="file-preview-name">{selectedFile.name}</p>
              <p className="file-preview-size">{formatFileSize(selectedFile.size)}</p>
            </div>
            <button
              className="remove-file"
              id="remove-file-btn"
              onClick={(e) => { e.stopPropagation(); setSelectedFile(null); }}
              aria-label="Remove selected file"
            >✕</button>
          </div>
        ) : (
          <>
            <div className="drop-icon">☁</div>
            <p className="drop-title">Drop your file here</p>
            <p className="drop-subtitle">or <span className="drop-browse">browse</span> to choose a file</p>
          </>
        )}
      </div>

      {/* Progress Bar */}
      {uploading && (
        <div className="progress-wrap" aria-live="polite">
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: `${progress}%` }} />
          </div>
          <span className="progress-label">{progress}%</span>
        </div>
      )}

      {/* Message */}
      {message && (
        <div className={`upload-message ${message.type}`} role="alert">
          <span className="msg-icon">{message.icon || (message.type === 'success' ? '✓' : '⚠')}</span>
          <div className="msg-body">
            <p className="msg-text">{message.text}</p>
            {message.hint && <p className="msg-hint">{message.hint}</p>}
          </div>
        </div>
      )}

      {/* Upload Button */}
      <button
        className="btn btn-primary upload-btn"
        id="upload-submit-btn"
        onClick={handleUpload}
        disabled={!selectedFile || uploading}
        aria-disabled={!selectedFile || uploading}
      >
        {uploading ? 'Uploading…' : 'Upload File'}
      </button>
    </div>
  );
}

export default FileUpload;
