import React, { useState, useEffect } from 'react';
import FileList from '../components/FileList';
import TimelineView from '../components/TimelineView';
import { getFiles, getTimeline } from '../services/api';
import { formatFileSize } from '../utils/helpers';
import './Dashboard.css';

function StatCard({ label, value, icon, accent }) {
  return (
    <div className={`stat-card card ${accent ? 'accent' : ''}`}>
      <span className="stat-icon">{icon}</span>
      <div>
        <p className="stat-value">{value}</p>
        <p className="stat-label">{label}</p>
      </div>
    </div>
  );
}

function Dashboard() {
  const [files, setFiles] = useState([]);
  const [timeline, setTimeline] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getFiles(), getTimeline()])
      .then(([f, t]) => { setFiles(f); setTimeline(t); })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const totalSize = files.reduce((acc, f) => acc + (f.size || 0), 0);
  const totalVersions = files.reduce((acc, f) => acc + (f.version || 1), 0);

  return (
    <div className="dashboard" id="dashboard-page">
      <div className="dashboard-hero">
        <h1 className="dashboard-heading">
          Welcome to <span className="gradient-text">FileVault</span>
        </h1>
        <p className="dashboard-subheading">
          Track, manage, and restore your file versions with ease.
        </p>
      </div>

      {/* Stats Row */}
      <div className="stats-row">
        <StatCard label="Total Files" value={loading ? '—' : files.length} icon="📁" accent />
        <StatCard label="Total Versions" value={loading ? '—' : totalVersions} icon="🔖" />
        <StatCard label="Storage Used" value={loading ? '—' : formatFileSize(totalSize)} icon="💾" />
        <StatCard label="Events" value={loading ? '—' : timeline.length} icon="⏱" />
      </div>

      {/* Content Grid */}
      <div className="dashboard-grid">
        <div className="card dashboard-files">
          <FileList files={files} loading={loading} />
        </div>
        <div className="card dashboard-timeline">
          <h3 className="section-title">Recent Activity</h3>
          <TimelineView events={timeline} />
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
