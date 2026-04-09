import React from 'react';
import './TimelineView.css';

function TimelineView({ events = [] }) {
  if (events.length === 0) {
    return (
      <div className="timeline empty-state">
        <span className="empty-icon">📅</span>
        <p>No timeline events yet.</p>
      </div>
    );
  }

  return (
    <div className="timeline" id="timeline-section" role="list" aria-label="File timeline">
      {events.map((event, idx) => (
        <div key={event.id || idx} className="timeline-event" id={`timeline-event-${idx}`} role="listitem">
          <div className="timeline-line" aria-hidden="true">
            <span className={`timeline-dot dot-${event.type || 'default'}`} />
            {idx < events.length - 1 && <div className="timeline-connector" />}
          </div>
          <div className="timeline-content card">
            <div className="timeline-event-header">
              <span className="timeline-event-type">{getEventLabel(event.type)}</span>
              <span className="timeline-event-time">{event.time}</span>
            </div>
            <p className="timeline-event-desc">{event.description}</p>
            {event.version && (
              <span className="badge badge-accent">v{event.version}</span>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

function getEventLabel(type) {
  const labels = {
    upload: '⬆ Upload',
    restore: '↩ Restore',
    delete: '🗑 Delete',
    edit: '✏ Edit',
    default: '• Event',
  };
  return labels[type] || labels.default;
}

export default TimelineView;
