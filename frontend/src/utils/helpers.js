// ── Date Formatting ───────────────────────────────

/**
 * Format an ISO date string into a human-readable format.
 * @param {string|Date} dateStr - ISO date string or Date object
 * @param {boolean} detailed - Include time if true
 * @returns {string}
 */
export function formatDate(dateStr, detailed = false) {
  if (!dateStr) return 'Unknown';
  const date = new Date(dateStr);
  if (isNaN(date)) return 'Invalid date';

  const opts = { year: 'numeric', month: 'short', day: 'numeric' };
  if (detailed) {
    opts.hour = '2-digit';
    opts.minute = '2-digit';
  }
  return date.toLocaleDateString('en-US', opts);
}

/**
 * Get a relative time string (e.g. "3 hours ago").
 * @param {string|Date} dateStr
 * @returns {string}
 */
export function timeAgo(dateStr) {
  if (!dateStr) return '';
  const diff = Date.now() - new Date(dateStr).getTime();
  const seconds = Math.floor(diff / 1000);
  if (seconds < 60)  return `${seconds}s ago`;
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60)  return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24)    return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

// ── File Size Formatting ──────────────────────────

/**
 * Convert bytes to a human-readable size string.
 * @param {number} bytes
 * @returns {string}
 */
export function formatFileSize(bytes) {
  if (bytes == null || bytes === 0) return '0 B';
  const units = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return `${(bytes / Math.pow(1024, i)).toFixed(i === 0 ? 0 : 1)} ${units[i]}`;
}

// ── File Type Helpers ─────────────────────────────

const EXT_ICONS = {
  pdf: '📄', doc: '📝', docx: '📝', xls: '📊', xlsx: '📊',
  ppt: '📊', pptx: '📊', txt: '📃', csv: '📊',
  jpg: '🖼', jpeg: '🖼', png: '🖼', gif: '🖼', svg: '🖼', webp: '🖼',
  mp4: '🎬', mov: '🎬', avi: '🎬',
  mp3: '🎵', wav: '🎵',
  zip: '🗜', rar: '🗜', gz: '🗜',
  js: '📜', ts: '📜', jsx: '📜', tsx: '📜',
  html: '🌐', css: '🎨', json: '📋', py: '🐍',
};

/**
 * Return an emoji icon for a file based on its extension.
 * @param {string} filename
 * @returns {string}
 */
export function getFileIcon(filename) {
  if (!filename) return '📁';
  const ext = filename.split('.').pop().toLowerCase();
  return EXT_ICONS[ext] || '📄';
}

/**
 * Extract the file extension from a filename.
 * @param {string} filename
 * @returns {string}
 */
export function getFileExtension(filename) {
  if (!filename || !filename.includes('.')) return '';
  return filename.split('.').pop().toLowerCase();
}

// ── Misc Utilities ────────────────────────────────

/**
 * Truncate a string to a given max length, appending '…' if truncated.
 * @param {string} str
 * @param {number} max
 * @returns {string}
 */
export function truncate(str, max = 40) {
  if (!str) return '';
  return str.length <= max ? str : `${str.slice(0, max)}…`;
}

/**
 * Generate a simple unique ID (for client-side use only).
 * @returns {string}
 */
export function generateId() {
  return `id-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;
}

/**
 * Download a Blob as a file.
 * @param {Blob} blob
 * @param {string} filename
 */
export function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}
