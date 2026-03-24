import axios from "axios";

const API_BASE = process.env.REACT_APP_API_URL || "/api";

const apiClient = axios.create({
  baseURL: API_BASE,
  headers: { "Content-Type": "application/json" },
});

// Attach JWT token to every request
apiClient.interceptors.request.use((config) => {
  const raw = localStorage.getItem("csrd-auth");
  if (raw) {
    try {
      const { state } = JSON.parse(raw);
      if (state?.token) {
        config.headers.Authorization = `Bearer ${state.token}`;
      }
    } catch (_) {}
  }
  return config;
});

// Handle 401 globally
apiClient.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem("csrd-auth");
      window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);

export default apiClient;

// ─── API helpers ────────────────────────────────────────────────────────────
export const authAPI = {
  register: (data) => apiClient.post("/auth/register", data),
  login: (username, password) =>
    apiClient.post(
      "/auth/login",
      new URLSearchParams({ username, password }),
      { headers: { "Content-Type": "application/x-www-form-urlencoded" } }
    ),
  getMe: () => apiClient.get("/auth/me"),
};

export const projectsAPI = {
  list: () => apiClient.get("/projects"),
  create: (data) => apiClient.post("/projects", data),
  get: (id) => apiClient.get(`/projects/${id}`),
  update: (id, data) => apiClient.put(`/projects/${id}`, data),
  delete: (id) => apiClient.delete(`/projects/${id}`),
  progress: (id) => apiClient.get(`/projects/${id}/progress`),
};

export const companyAPI = {
  get: () => apiClient.get("/company"),
  update: (data) => apiClient.put("/company", data),
};

export const emissionsAPI = {
  list: (projectId) => apiClient.get(`/projects/${projectId}/emissions`),
  create: (projectId, data) => apiClient.post(`/projects/${projectId}/emissions`, data),
  delete: (projectId, entryId) => apiClient.delete(`/projects/${projectId}/emissions/${entryId}`),
  summary: (projectId) => apiClient.get(`/projects/${projectId}/emissions/summary`),
  factors: (projectId) => apiClient.get(`/projects/${projectId}/emissions/emission-factors`),
  scope3Categories: (projectId) => apiClient.get(`/projects/${projectId}/emissions/scope3-categories`),
};

export const materialityAPI = {
  topics: (projectId) => apiClient.get(`/projects/${projectId}/materiality/topics`),
  updateTopic: (projectId, topicId, data) =>
    apiClient.put(`/projects/${projectId}/materiality/topics/${topicId}`, data),
  heatmap: (projectId) => apiClient.get(`/projects/${projectId}/materiality/heatmap`),
  materialTopics: (projectId) => apiClient.get(`/projects/${projectId}/materiality/material-topics`),
  complete: (projectId) => apiClient.post(`/projects/${projectId}/materiality/complete`),
};

export const iroAPI = {
  list: (projectId) => apiClient.get(`/projects/${projectId}/iro`),
  create: (projectId, data) => apiClient.post(`/projects/${projectId}/iro`, data),
  delete: (projectId, iroId) => apiClient.delete(`/projects/${projectId}/iro/${iroId}`),
  summary: (projectId) => apiClient.get(`/projects/${projectId}/iro/summary`),
  taxonomy: (projectId) => apiClient.get(`/projects/${projectId}/iro/risk-taxonomy`),
};

export const scenarioAPI = {
  ngfsScenarios: (projectId) => apiClient.get(`/projects/${projectId}/scenarios/ngfs`),
  run: (projectId, data) => apiClient.post(`/projects/${projectId}/scenarios/run`, data),
};

export const reportsAPI = {
  list: (projectId) => apiClient.get(`/projects/${projectId}/reports`),
  generate: (projectId, data) => apiClient.post(`/projects/${projectId}/reports/generate`, data),
  get: (projectId, reportId) => apiClient.get(`/projects/${projectId}/reports/${reportId}`),
  downloadUrl: (projectId, reportId, format) =>
    `${API_BASE}/projects/${projectId}/reports/${reportId}/download/${format}`,
};

export const dataAPI = {
  list: (projectId, standard) =>
    apiClient.get(`/projects/${projectId}/data${standard ? `?esrs_standard=${standard}` : ""}`),
  create: (projectId, data) => apiClient.post(`/projects/${projectId}/data`, data),
  esrsStructure: (projectId) => apiClient.get(`/projects/${projectId}/data/esrs-structure`),
};
