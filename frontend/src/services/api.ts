import axios from 'axios';

// Dynamically determine the base URL of the FastAPI backend.
// In dev (port 5173), point explicitly to localhost:8000.
// In production (same origin), use relative path.
const API_BASE = import.meta.env.VITE_API_URL || 
  (window.location.port === '5173' ? `http://${window.location.hostname}:8000` : '');

export const api = axios.create({
  baseURL: `${API_BASE}/api`,
  timeout: 30000, // 30 seconds timeout for inference and report generation
});

export const getStaticUrl = (path: string) => {
  if (!path) return '';
  // Static files are served at /static on the backend
  return `${API_BASE}${path}`;
};
