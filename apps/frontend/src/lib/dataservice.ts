import type { JobData, JobCreatePayload, JobUpdatePayload, BoardData, DashboardStats } from './types';
import { useAuthStore } from '@/stores/auth';
import router from '@/router';
import { toast } from 'vue-sonner';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

function authHeaders(): Record<string, string> {
  return useAuthStore().getAuthHeaders();
}

// Singleton promise — if multiple requests fail with 401 simultaneously,
// they all wait on the same refresh attempt instead of hammering the endpoint.
let refreshPromise: Promise<boolean> | null = null;

async function tryRefreshToken(): Promise<boolean> {
  if (refreshPromise) return refreshPromise;

  const refreshToken = localStorage.getItem('refresh_token');
  if (!refreshToken) return false;

  refreshPromise = fetch(`${API_BASE}/auth/refresh`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: refreshToken }),
  })
    .then(async (res) => {
      if (!res.ok) return false;
      const data = await res.json();
      if (data.access_token) {
        useAuthStore().setTokens(data.access_token);
        return true;
      }
      return false;
    })
    .catch(() => false)
    .finally(() => { refreshPromise = null; });

  return refreshPromise;
}

function onUnauthorized() {
  useAuthStore().clearAuth();
  toast.error('Session expired. Please sign in again.');
  router.replace('/login');
}

async function apiFetch(url: string, options: RequestInit = {}): Promise<Response> {
  let response = await fetch(url, options);

  if (response.status === 401) {
    const refreshed = await tryRefreshToken();
    if (refreshed) {
      // Retry with the fresh access token
      response = await fetch(url, {
        ...options,
        headers: { ...(options.headers as Record<string, string>), ...authHeaders() },
      });
    }
    if (response.status === 401) {
      onUnauthorized();
    }
  }

  return response;
}

export interface JobFilters {
  query?: string
  title?: string
  company?: string
  location?: string
  status?: string
  source_platform?: string
  board_id?: number
  page?: number
  per_page?: number
}

export interface PaginatedJobs {
  items: JobData[]
  total: number
  page: number
  per_page: number
  total_pages: number
}

function toFrontendPaginated(data: { meta: Record<string, number>; results: JobData[] }): PaginatedJobs {
  return {
    items: data.results,
    total: data.meta.total,
    page: data.meta.page,
    per_page: data.meta.per_page,
    total_pages: data.meta.total_pages,
  };
}

export default {
  async getJobs(filters: JobFilters = {}): Promise<PaginatedJobs> {
    const params = new URLSearchParams();
    if (filters.query) params.set('query', filters.query);
    if (filters.title) params.set('title', filters.title);
    if (filters.company) params.set('company', filters.company);
    if (filters.location) params.set('location', filters.location);
    if (filters.status) params.set('status', filters.status);
    if (filters.source_platform) params.set('source_platform', filters.source_platform);
    if (filters.board_id) params.set('board_id', String(filters.board_id));
    if (filters.page) params.set('page', String(filters.page));
    if (filters.per_page) params.set('per_page', String(filters.per_page));

    const response = await apiFetch(`${API_BASE}/jobs?${params.toString()}`, {
      headers: { ...authHeaders() },
    });
    if (!response.ok) {
      return { items: [], total: 0, page: 1, per_page: 20, total_pages: 0 };
    }
    return toFrontendPaginated(await response.json());
  },

  async getJob(jobId: number): Promise<JobData | null> {
    const response = await apiFetch(`${API_BASE}/jobs/${jobId}`, {
      headers: { ...authHeaders() },
    });
    if (!response.ok) return null;
    return response.json();
  },

  async createJob(payload: JobCreatePayload): Promise<JobData | null> {
    const response = await apiFetch(`${API_BASE}/jobs/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...authHeaders() },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      console.error('Failed to create job', await response.json().catch(() => {}));
      return null;
    }
    return response.json();
  },

  async updateJob(jobId: number, payload: JobUpdatePayload): Promise<JobData | null> {
    const response = await apiFetch(`${API_BASE}/jobs/${jobId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json', ...authHeaders() },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      console.error('Failed to update job', await response.json().catch(() => {}));
      return null;
    }
    return response.json();
  },

  async deleteJob(jobId: number): Promise<boolean> {
    const response = await apiFetch(`${API_BASE}/jobs/${jobId}`, {
      method: 'DELETE',
      headers: { ...authHeaders() },
    });
    return response.ok;
  },

  async getBoards(): Promise<BoardData[]> {
    const response = await apiFetch(`${API_BASE}/boards`, {
      headers: { ...authHeaders() },
    });
    if (!response.ok) return [];
    return response.json();
  },

  async getBoard(boardId: number): Promise<BoardData | null> {
    const response = await apiFetch(`${API_BASE}/boards/${boardId}`, {
      headers: { ...authHeaders() },
    });
    if (!response.ok) return null;
    return response.json();
  },

  async createBoard(payload: { name: string; color?: string; description?: string; stages?: { key: string; label: string; color: string }[] }): Promise<BoardData | null> {
    const response = await apiFetch(`${API_BASE}/boards`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...authHeaders() },
      body: JSON.stringify(payload),
    });
    if (!response.ok) return null;
    return response.json();
  },

  async updateBoard(boardId: number, payload: { name?: string; color?: string; description?: string; stages?: { key: string; label: string; color: string }[]; key_renames?: Record<string, string> }): Promise<BoardData | null> {
    const response = await apiFetch(`${API_BASE}/boards/${boardId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json', ...authHeaders() },
      body: JSON.stringify(payload),
    });
    if (!response.ok) return null;
    return response.json();
  },

  async setDefaultBoard(boardId: number): Promise<BoardData | null> {
    const response = await apiFetch(`${API_BASE}/boards/${boardId}/set-default`, {
      method: 'POST',
      headers: { ...authHeaders() },
    });
    if (!response.ok) return null;
    return response.json();
  },

  async deleteBoard(boardId: number): Promise<boolean> {
    const response = await apiFetch(`${API_BASE}/boards/${boardId}`, {
      method: 'DELETE',
      headers: { ...authHeaders() },
    });
    return response.ok;
  },

  async getDashboardStats(): Promise<DashboardStats | null> {
    const response = await apiFetch(`${API_BASE}/dashboard/stats`, {
      headers: { ...authHeaders() },
    });
    if (!response.ok) return null;
    return response.json();
  },
};
