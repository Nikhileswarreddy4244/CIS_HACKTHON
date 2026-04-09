import axios from 'axios';

const BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

// ── Interceptors ──────────────────────────────────
api.interceptors.response.use(
  res => res.data,
  err => {
    // FastAPI returns errors as { detail: "..." }
    // Preserve both the human-readable message AND the HTTP status code
    const detail = err.response?.data?.detail;
    const status = err.response?.status;
    const enhanced = new Error(detail || err.message || 'Something went wrong.');
    enhanced.status = status;
    enhanced.detail = detail;
    return Promise.reject(enhanced);
  }
);


// ── Files ─────────────────────────────────────────

/** Fetch all files */
export const getFiles = () => api.get('/files');

/** Upload a new file (or new version of existing) */
export const uploadFile = (file, onUploadProgress) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/files/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress,
  });
};

/** Delete a file by ID */
export const deleteFile = (fileId) => api.delete(`/files/${fileId}`);

/** Download the current version of a file as a blob */
export const downloadFile = (fileId) =>
  api.get(`/files/${fileId}/download`, { responseType: 'blob' });

// ── Versions ──────────────────────────────────────

/** Get all versions for a file */
export const getVersions = (fileId) => api.get(`/files/${fileId}/versions`);

/** Restore a specific version */
export const restoreVersion = (fileId, versionId) =>
  api.post(`/files/${fileId}/versions/${versionId}/restore`);

/** Download a specific version */
export const downloadVersion = (fileId, versionId) =>
  api.get(`/files/${fileId}/versions/${versionId}/download`, { responseType: 'blob' });

// ── Timeline ──────────────────────────────────────

/** Get global activity timeline */
export const getTimeline = () => api.get('/timeline');

export default api;
