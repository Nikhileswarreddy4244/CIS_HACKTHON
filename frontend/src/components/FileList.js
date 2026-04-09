import React, { useState } from 'react';
import { formatFileSize, formatDate, getFileIcon, downloadBlob } from '../utils/helpers';
import { downloadFile } from '../services/api';
import './FileList.css';

function FileList({ files = [], loading, onSelect, onDelete, selectedId }) {
  const [search, setSearch] = useState('');
  const [downloading, setDownloading] = useState(null); // tracks which file is downloading

  const handleDownload = async (e, file) => {
    e.stopPropagation(); // don't trigger row selection
    setDownloading(file.id);
    try {
      const blob = await downloadFile(file.id);
      downloadBlob(blob, file.original_name || file.name);
    } catch (err) {
      alert('Download failed: ' + err.message);
    } finally {
      setDownloading(null);
    }
  };

  const filtered = files.filter(f =>
    f.name.toLowerCase().includes(search.toLowerCase())
  );

  if (loading) {
    return (
      <div className="file-list-skeleton" aria-busy="true" aria-label="Loading files">
        {[1, 2, 3].map(i => (
          <div key={i} className="skeleton-row" />
        ))}
      </div>
    );
  }

  return (
    <div className="file-list" id="file-list-section">
      {/* Search */}
      <div className="file-list-header">
        <h2 className="file-list-title">Files</h2>
        <input
          className="file-search"
          id="file-search-input"
          type="search"
          placeholder="Search files…"
          value={search}
          onChange={e => setSearch(e.target.value)}
          aria-label="Search files"
        />
      </div>

      {filtered.length === 0 ? (
        <div className="empty-state">
          <span className="empty-icon">📂</span>
          <p>{search ? 'No files match your search.' : 'No files uploaded yet.'}</p>
        </div>
      ) : (
        <ul className="file-items">
          {filtered.map(file => (
            <li
              key={file.id}
              className={`file-item ${selectedId === file.id ? 'selected' : ''}`}
              id={`file-item-${file.id}`}
              onClick={() => onSelect?.(file)}
              role="button"
              tabIndex={0}
              onKeyDown={e => e.key === 'Enter' && onSelect?.(file)}
            >
              <span className="file-item-icon">{getFileIcon(file.name)}</span>
              <div className="file-item-info">
                <p className="file-item-name">{file.name}</p>
                <p className="file-item-meta">
                  {formatFileSize(file.size)} · {formatDate(file.updatedAt)} · v{file.version}
                </p>
              </div>
              <div className="file-item-actions">
                <span className="badge badge-accent">v{file.version || file.current_version}</span>
                <button
                  className="btn file-download-btn"
                  id={`download-file-${file.id}`}
                  onClick={(e) => handleDownload(e, file)}
                  disabled={downloading === file.id}
                  aria-label={`Download ${file.name}`}
                  title="Download current version"
                >
                  {downloading === file.id ? '…' : '⬇'}
                </button>
                {onDelete && (
                  <button
                    className="btn btn-danger file-delete-btn"
                    id={`delete-file-${file.id}`}
                    onClick={e => { e.stopPropagation(); onDelete(file); }}
                    aria-label={`Delete ${file.name}`}
                  >
                    🗑
                  </button>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default FileList;
