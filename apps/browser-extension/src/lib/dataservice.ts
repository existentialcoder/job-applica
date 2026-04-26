import ext from './ext';

const API_BASE = 'http://localhost:8000/api/v1';

// ── Storage helpers ───────────────────────────────────────────────────────────

const storage = {
  async get(key: string): Promise<string | null> {
    const result = await ext.storage.local.get([key]);
    return (result[key] as string) || null;
  },
  async set(key: string, value: string): Promise<void> {
    await ext.storage.local.set({ [key]: value });
  },
  async remove(key: string): Promise<void> {
    await ext.storage.local.remove(key);
  },
};

// ── Types ─────────────────────────────────────────────────────────────────────

export interface StageData {
  key: string;
  label: string;
  color: string;
}

export interface BoardData {
  id: number;
  name: string;
  color?: string;
  stages: StageData[];
  is_default: boolean;
}

export interface JobData {
  title: string;
  company_name?: string;
  location?: string;
  status: string;
  category?: string;
  salary_range?: string;
  required_skills?: string[];
  description?: string;
  work_model?: string;
  source_url?: string;
  source_platform?: string;
  applied_date?: string;
  notes?: string;
  board_id?: number;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
}

async function refreshAccessToken(): Promise<string | null> {
  const refreshToken = await storage.get('refresh_token');
  if (!refreshToken) return null;
  try {
    const response = await fetch(`${API_BASE}/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
    if (!response.ok) return null;
    const data = await response.json();
    if (data.access_token) {
      await storage.set('access_token', data.access_token);
      return data.access_token;
    }
  } catch { }
  return null;
}

async function authedFetch(url: string, options: RequestInit = {}): Promise<Response> {
  const token = await storage.get('access_token');
  const baseHeaders: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
  let response = await fetch(url, { ...options, headers: baseHeaders });
  if (response.status === 401) {
    const newToken = await refreshAccessToken();
    if (newToken) {
      response = await fetch(url, {
        ...options,
        headers: { ...baseHeaders, Authorization: `Bearer ${newToken}` },
      });
    }
  }
  return response;
}

// ── Exported service ──────────────────────────────────────────────────────────

export default {
  // ── Auth ──────────────────────────────────────────────────────────────────

  async login(username: string, password: string): Promise<boolean> {
    const body = new URLSearchParams();
    body.append('username', username);
    body.append('password', password);

    const response = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: body.toString(),
    });

    if (!response.ok) return false;

    const data: AuthTokens & { message: string } = await response.json();
    await storage.set('access_token', data.access_token);
    await storage.set('refresh_token', data.refresh_token);
    return true;
  },

  async logout(): Promise<void> {
    await storage.remove('access_token');
    await storage.remove('refresh_token');
  },

  async isLoggedIn(): Promise<boolean> {
    const token = await storage.get('access_token');
    return !!token;
  },

  // ── Tab / URL helpers ─────────────────────────────────────────────────────

  async getCurrentTabUrl(): Promise<string | null> {
    const tabs = await ext.tabs.query({ active: true, currentWindow: true });
    return tabs[0]?.url || null;
  },

  detectPlatform(url: string): string | null {
    if (url.includes('linkedin.com')) return 'LinkedIn';
    if (url.includes('indeed.com')) return 'Indeed';
    if (url.includes('glassdoor.com')) return 'Glassdoor';
    if (url.includes('monster.com')) return 'Monster';
    if (url.includes('ziprecruiter.com')) return 'ZipRecruiter';
    if (url.includes('jobscan.co')) return 'Jobscan';
    return null;
  },

  isJobPage(url: string): boolean {
    if (url.includes('linkedin.com') && url.includes('/jobs')) return true;
    if (url.includes('indeed.com') && (
      url.includes('/viewjob') || url.includes('/rc/clk') ||
      url.includes('/applystart') || url.includes('vjk=') || url.includes('/jobs?')
    )) return true;
    if (url.includes('glassdoor.com') && (
      url.includes('/job-listing') || url.includes('/job/') || url.includes('/Jobs/')
    )) return true;
    if (url.includes('monster.com') && url.includes('/job')) return true;
    if (url.includes('ziprecruiter.com') && (url.includes('/jobs') || url.includes('/c/'))) return true;
    if (url.includes('jobscan.co')) return true;
    return false;
  },

  async fetchJobDataFromContentScript(): Promise<void> {
    const tabs = await ext.tabs.query({ active: true, currentWindow: true });
    const tabId = tabs[0]?.id;
    if (!tabId) return;

    const url = tabs[0]?.url || '';
    let scriptFile = 'content/linkedin.js';
    if (url.includes('indeed.com')) scriptFile = 'content/indeed.js';
    else if (url.includes('glassdoor.com')) scriptFile = 'content/glassdoor.js';
    else if (url.includes('monster.com')) scriptFile = 'content/monster.js';
    else if (url.includes('ziprecruiter.com')) scriptFile = 'content/ziprecruiter.js';
    else if (url.includes('jobscan.co')) scriptFile = 'content/jobscan.js';

    await ext.scripting.executeScript({ target: { tabId }, files: [scriptFile] });
  },

  // ── API calls ─────────────────────────────────────────────────────────────

  async checkJobExists(title: string, company?: string): Promise<number | null> {
    const params = new URLSearchParams({ title });
    if (company) params.set('company', company);
    const response = await authedFetch(`${API_BASE}/jobs?${params}`);
    if (!response.ok) return null;
    const data = await response.json();
    return data?.results?.[0]?.id ?? null;
  },

  // Pull the web app's localStorage token into extension storage.
  // Called on popup open when no token is stored in the extension.
  async syncFromWebApp(): Promise<boolean> {
    try {
      const tabs = await ext.tabs.query({ url: 'http://localhost:5173/*' });
      for (const tab of tabs || []) {
        if (!tab.id) continue;
        const [result] = await ext.scripting.executeScript({
          target: { tabId: tab.id },
          func: () => ({
            access_token: localStorage.getItem('access_token') || null,
            refresh_token: localStorage.getItem('refresh_token') || null,
          }),
        });
        const tokens = result?.result as { access_token: string | null; refresh_token: string | null } | undefined;
        if (tokens?.access_token) {
          await ext.storage.local.set({ access_token: tokens.access_token });
          if (tokens.refresh_token) await ext.storage.local.set({ refresh_token: tokens.refresh_token });
          return true;
        }
      }
    } catch { }
    return false;
  },

  async createJob(jobData: JobData): Promise<number | null> {
    const response = await authedFetch(`${API_BASE}/jobs/`, {
      method: 'POST',
      body: JSON.stringify(jobData),
    });
    if (!response.ok) {
      console.error('Job creation failed:', await response.json().catch(() => {}));
      return null;
    }
    const data = await response.json();
    return data?.id ?? null;
  },

  async updateJobStatus(jobId: number, status: string): Promise<boolean> {
    const response = await authedFetch(`${API_BASE}/jobs/${jobId}`, {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    });
    return response.ok;
  },

  // ── User settings ─────────────────────────────────────────────────────────

  async getSettings(): Promise<Record<string, any>> {
    const token = await storage.get('access_token');
    if (!token) return {};
    const response = await authedFetch(`${API_BASE}/auth/settings`);
    if (!response.ok) return {};
    const data = await response.json();
    return data.settings ?? {};
  },

  async updateSettings(patch: Record<string, any>): Promise<void> {
    const token = await storage.get('access_token');
    if (!token) return;
    await authedFetch(`${API_BASE}/auth/settings`, {
      method: 'PATCH',
      body: JSON.stringify({ settings: patch }),
    });
  },

  // ── Boards ────────────────────────────────────────────────────────────────

  async getBoards(): Promise<BoardData[]> {
    const response = await authedFetch(`${API_BASE}/boards`);
    if (!response.ok) return [];
    return response.json();
  },

  async getBoard(boardId: number): Promise<BoardData | null> {
    const response = await authedFetch(`${API_BASE}/boards/${boardId}`);
    if (!response.ok) return null;
    return response.json();
  },
};
