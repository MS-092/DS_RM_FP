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

export default api;
