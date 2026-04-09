import React, { useState } from 'react';
import FileUpload from '../components/FileUpload';
import FileList from '../components/FileList';
import { getFiles } from '../services/api';
import './UploadPage.css';

function UploadPage() {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchFiles = () => {
    setLoading(true);
    getFiles()
      .then(setFiles)
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  return (
    <div className="upload-page" id="upload-page">
      <div className="page-header">
        <h1 className="page-title gradient-text">Upload Files</h1>
        <p className="page-subtitle">
          Drop a new file or a new version of an existing file. All versions are preserved.
        </p>
      </div>

      <div className="upload-layout">
        <div className="card upload-card">
          <h2 className="card-title">New Upload</h2>
          <FileUpload onUploadSuccess={fetchFiles} />
        </div>
        <div className="card recent-uploads-card">
          <h2 className="card-title">Recent Files</h2>
          <FileList files={files} loading={loading} />
        </div>
      </div>
    </div>
  );
}

export default UploadPage;
