const API_BASE = 'http://localhost:8000';

class JALocalStorage {
    static async getItem(key: string): Promise<string | null> {
        if (typeof chrome !== 'undefined' && chrome.storage?.local) {
            return new Promise((resolve) => {
                chrome.storage.local.get([key], (result) => resolve(result[key] || null));
            });
        } else if (typeof browser !== 'undefined' && browser.storage?.local) {
            const result = await browser.storage.local.get(key);
            return result[key] || null;
        }
        return null;
    }

    static async setItem(key: string, value: string): Promise<void> {
        if (typeof chrome !== 'undefined' && chrome.storage?.local) {
            await chrome.storage.local.set({ [key]: value });
        } else if (typeof browser !== 'undefined' && browser.storage?.local) {
            await browser.storage.local.set({ [key]: value });
        }
    }

    static async removeItem(key: string): Promise<void> {
        if (typeof chrome !== 'undefined' && chrome.storage?.local) {
            await chrome.storage.local.remove(key);
        } else if (typeof browser !== 'undefined' && browser.storage?.local) {
            await browser.storage.local.remove(key);
        }
    }
}

interface JobData {
    job_title: string
    company?: string
    location?: string,
    status: string
    category?: string
    salary_range?: string
    required_skills?: string[]
    job_description?: string
    min_years_of_experience?: number
    max_years_of_experience?: number
};

export default {
    async getUserName(): Promise<string> {
        const userName = await JALocalStorage.getItem('userName');
        return userName || 'Guest';
    },

    async getAppSettings(): Promise<object> {
        const appSettings = await JALocalStorage.getItem('appSettings');
        return appSettings ? JSON.parse(appSettings) : {};
    },

    async getCurrentTabUrl(): Promise<string | null> {
        if (typeof chrome !== 'undefined' && chrome.tabs) {
            return new Promise((resolve) => {
                chrome.tabs.query({ active: true, currentWindow: true }, (tabs) =>
                    resolve(tabs[0]?.url || null)
                );
            });
        } else if (typeof browser !== 'undefined' && browser.tabs) {
            const tabs = await browser.tabs.query({ active: true, currentWindow: true });
            return tabs[0]?.url || null;
        }
        return null;
    },

    async fetchJobDataFromContentScript(tabId?: number) {
        if (!tabId) {
            const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
            tabId = tabs[0]?.id;
            if (!tabId) return;
        }

        await chrome.scripting.executeScript({
            target: { tabId },
            files: ['content.js']
        });
    },

    async createJob(jobData: JobData) {
        const url = `${API_BASE}/jobs`;
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(jobData)
        });

        if (!response.ok) {
            const err = await response.json();
            console.error('Job creation failed:', err);
        }

        return response.ok; // returns true if 2xx status
    },
    async getJobs(): Promise<Array<{ id: string; title: string; company: string; link: string; status: string }>> {
        const jobsStr = await JALocalStorage.getItem('jobs');
        return jobsStr ? JSON.parse(jobsStr) : [];
    },

    async removeJob(jobId: string) {
        const jobsStr = await JALocalStorage.getItem('jobs');
        const jobs = jobsStr ? JSON.parse(jobsStr) : [];
        const filtered = jobs.filter((j: any) => j.id !== jobId);
        await JALocalStorage.setItem('jobs', JSON.stringify(filtered));
    },

    async updateJob(updatedJob: { id: string; title: string; company: string; link: string; status: string }) {
        const jobsStr = await JALocalStorage.getItem('jobs');
        const jobs = jobsStr ? JSON.parse(jobsStr) : [];
        const updatedJobs = jobs.map((j: any) => (j.id === updatedJob.id ? updatedJob : j));
        await JALocalStorage.setItem('jobs', JSON.stringify(updatedJobs));
    }
};
