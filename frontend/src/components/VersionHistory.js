import React, { useState } from 'react';
import { formatDate, formatFileSize, downloadBlob } from '../utils/helpers';
import { downloadVersion } from '../services/api';
import './VersionHistory.css';

function VersionHistory({ versions = [], loading, onRestore, currentVersion, fileId, fileName }) {
  const [downloading, setDownloading] = useState(null);

  const handleDownload = async (e, version) => {
    e.stopPropagation();
    setDownloading(version.id);
    try {
      const blob = await downloadVersion(fileId, version.id);
      downloadBlob(blob, `v${version.version_number}_${fileName || 'file'}`);
    } catch (err) {
      alert('Download failed: ' + err.message);
    } finally {
      setDownloading(null);
    }
  };

  if (loading) {
    return (
      <div className="version-history" aria-busy="true">
        {[1, 2, 3].map(i => <div key={i} className="skeleton-row" />)}
      </div>
    );
  }

  if (versions.length === 0) {
    return (
      <div className="version-history empty-state">
        <span className="empty-icon">🕰</span>
        <p>No version history available.</p>
      </div>
    );
  }

  return (
    <div className="version-history" id="version-history-section">
      <h3 className="version-history-title">Version History</h3>
      <ul className="version-list" role="list">
        {versions.map((v, idx) => (
          <li key={v.id} className={`version-item ${v.version === currentVersion ? 'current' : ''}`} id={`version-${v.id}`}>
            <div className="version-dot" aria-hidden="true" />
            <div className="version-body">
              <div className="version-header">
                <span className="version-tag">v{v.version}</span>
                {v.version === currentVersion && (
                  <span className="badge badge-success">Current</span>
                )}
                {idx === 0 && v.version !== currentVersion && (
                  <span className="badge badge-warning">Latest</span>
                )}
              </div>
              <p className="version-date">{formatDate(v.createdAt, true)}</p>
              <p className="version-size">{formatFileSize(v.size)} · {v.author || 'Unknown'}</p>
              {v.message && <p className="version-message">"{v.message}"</p>}
            </div>
            <div className="version-actions">
              <button
                className="btn btn-secondary version-dl-btn"
                id={`download-version-${v.id}`}
                onClick={(e) => handleDownload(e, v)}
                disabled={downloading === v.id}
                title={`Download v${v.version_number}`}
                aria-label={`Download version ${v.version_number}`}
              >
                {downloading === v.id ? '…' : '⬇ Download'}
              </button>
              {v.version !== currentVersion && (
                <button
                  className="btn btn-secondary restore-btn"
                  id={`restore-btn-${v.id}`}
                  onClick={() => onRestore?.(v)}
                  aria-label={`Restore version ${v.version}`}
                >
                  ↩ Restore
                </button>
              )}
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default VersionHistory;
