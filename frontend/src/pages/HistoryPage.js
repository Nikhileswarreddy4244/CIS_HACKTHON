import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import FileList from '../components/FileList';
import VersionHistory from '../components/VersionHistory';
import RestoreModal from '../components/RestoreModal';
import { getFiles, getVersions, restoreVersion } from '../services/api';
import './HistoryPage.css';

function HistoryPage() {
  const { fileId } = useParams();
  const [files, setFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [versions, setVersions] = useState([]);
  const [loadingFiles, setLoadingFiles] = useState(true);
  const [loadingVersions, setLoadingVersions] = useState(false);
  const [restoreTarget, setRestoreTarget] = useState(null);

  // Load files on mount
  useEffect(() => {
    getFiles()
      .then(f => {
        setFiles(f);
        if (fileId) {
          const match = f.find(fi => fi.id === fileId);
          if (match) handleSelectFile(match);
        }
      })
      .catch(console.error)
      .finally(() => setLoadingFiles(false));
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleSelectFile = (file) => {
    setSelectedFile(file);
    setLoadingVersions(true);
    getVersions(file.id)
      .then(setVersions)
      .catch(console.error)
      .finally(() => setLoadingVersions(false));
  };

  const handleRestore = async (version) => {
    try {
      await restoreVersion(selectedFile.id, version.id);
      handleSelectFile(selectedFile); // refresh
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="history-page" id="history-page">
      <div className="page-header">
        <h1 className="page-title gradient-text">Version History</h1>
        <p className="page-subtitle">Select a file to explore its full version timeline.</p>
      </div>

      <div className="history-layout">
        {/* File picker */}
        <div className="card history-files-panel">
          <FileList
            files={files}
            loading={loadingFiles}
            onSelect={handleSelectFile}
            selectedId={selectedFile?.id}
          />
        </div>

        {/* Version panel */}
        <div className="card history-versions-panel">
          {selectedFile ? (
            <>
              <div className="versions-header">
                <h2 className="panel-title">{selectedFile.name}</h2>
                <span className="badge badge-accent">v{selectedFile.version} versions</span>
              </div>
              <VersionHistory
                versions={versions}
                loading={loadingVersions}
                currentVersion={selectedFile.version || selectedFile.current_version}
                onRestore={v => setRestoreTarget(v)}
                fileId={selectedFile.id}
                fileName={selectedFile.original_name || selectedFile.name}
              />
            </>
          ) : (
            <div className="empty-state">
              <span className="empty-icon">←</span>
              <p>Select a file to view its history.</p>
            </div>
          )}
        </div>
      </div>

      {/* Restore confirmation modal */}
      <RestoreModal
        isOpen={!!restoreTarget}
        version={restoreTarget}
        fileName={selectedFile?.name}
        onConfirm={handleRestore}
        onClose={() => setRestoreTarget(null)}
      />
    </div>
  );
}

export default HistoryPage;
