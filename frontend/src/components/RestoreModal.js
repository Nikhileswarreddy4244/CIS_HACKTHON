import React from 'react';
import './RestoreModal.css';

function RestoreModal({ isOpen, version, fileName, onConfirm, onClose }) {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay" role="dialog" aria-modal="true" aria-labelledby="restore-modal-title" id="restore-modal">
      <div className="modal-backdrop" onClick={onClose} aria-hidden="true" />
      <div className="modal-box">
        <button className="modal-close" id="modal-close-btn" onClick={onClose} aria-label="Close modal">✕</button>
        <div className="modal-icon">↩</div>
        <h2 className="modal-title" id="restore-modal-title">Restore Version</h2>
        <p className="modal-body">
          You are about to restore <strong>{fileName}</strong> to{' '}
          <strong>version {version?.version}</strong>. This will create a new version
          with the restored content.
        </p>
        <div className="modal-actions">
          <button className="btn btn-secondary" id="modal-cancel-btn" onClick={onClose}>
            Cancel
          </button>
          <button className="btn btn-primary" id="modal-confirm-btn" onClick={() => { onConfirm?.(version); onClose(); }}>
            ↩ Confirm Restore
          </button>
        </div>
      </div>
    </div>
  );
}

export default RestoreModal;
