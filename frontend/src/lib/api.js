import axios from 'axios';

// Use empty string for production (Docker/Kubernetes) to rely on relative paths (handled by Ingress/Nginx)
// Use localhost:8000 for local dev (npm run dev)
const API_BASE_URL = import.meta.env.MODE === 'production' ? '' : 'http://localhost:8000';



const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor to add JWT token
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Auth API
export const authApi = {
    login: (username, password) => {
        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);
        return api.post('/api/auth/login', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        });
    },
    register: (data) => api.post('/api/auth/register', data),
    me: () => api.get('/api/auth/me'), // Assuming you might have a /me endpoint or similar
};

// Issues API
export const issuesApi = {
    getAll: () => api.get('/api/issues/'),
    getById: (id) => api.get(`/api/issues/${id}`),
    create: (data) => api.post('/api/issues/', data),
    delete: (id) => api.delete(`/api/issues/${id}`),
};

// Comments API
export const commentsApi = {
    getByIssueId: (issueId) => api.get(`/api/comments/issue/${issueId}`),
    create: (data) => api.post('/api/comments/', data),
    delete: (id) => api.delete(`/api/comments/${id}`),
};

// Repositories API
export const repositoriesApi = {
    getAll: () => api.get('/api/repositories'),
    getById: (owner, repo) => api.get(`/api/repositories/${owner}/${repo}`),
    getContents: (owner, repo, path = '') => {
        // Ensure trailing slash for root directory
        const contentPath = path ? `/api/repositories/${owner}/${repo}/contents/${path}` : `/api/repositories/${owner}/${repo}/contents/`;
        return api.get(contentPath);
    },
    getFile: (owner, repo, path) => api.get(`/api/repositories/${owner}/${repo}/file/${path}`),
    getBranches: (owner, repo) => api.get(`/api/repositories/${owner}/${repo}/branches`),
    getIssues: (owner, repo) => api.get(`/api/repositories/${owner}/${repo}/issues`),
};

// Health API
export const healthApi = {
    check: () => api.get('/api/health'),
};

// Fault Tolerance API
export const faultToleranceApi = {
    getStatus: () => api.get('/api/fault-tolerance/status'),
    configure: (config) => api.post('/api/fault-tolerance/configure', config),
    simulateFailure: (data) => api.post('/api/fault-tolerance/simulate-failure', data),
    runExperiment: (data) => api.post('/api/fault-tolerance/run-experiment', data),
};

export default api;
