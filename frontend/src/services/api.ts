import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const uploadVideo = async (
  file: File,
  onProgress: (progress: number) => void
): Promise<string> => {
  const formData = new FormData();
  formData.append('video', file);

  const response = await api.post('/api/v1/videos/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    onUploadProgress: (progressEvent) => {
      if (progressEvent.total) {
        const percentCompleted = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        );
        onProgress(percentCompleted);
      }
    },
  });

  return response.data.session_id;
};

export const getAnalysisResults = async (sessionId: string): Promise<any> => {
  const response = await api.get(`/api/v1/analysis/${sessionId}/results`);
  return response.data;
};

export const getAnalysisStatus = async (sessionId: string): Promise<any> => {
  const response = await api.get(`/api/v1/analysis/${sessionId}/status`);
  return response.data;
};

export default api;
