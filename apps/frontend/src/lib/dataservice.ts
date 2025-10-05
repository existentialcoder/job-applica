import type { JobData } from './types';

const API_BASE = 'http://localhost:8000';

export default {
    async getJobs(): Promise<JobData[]> {
        const response = await fetch(`${API_BASE}/jobs`);
        if (!response.ok) {
            console.error('Failed to fetch jobs');
            return [];
        }
        return response.json();
    },
    async deleteJob(jobId: number): Promise<void> {
        const response = await fetch(`${API_BASE}/jobs/${jobId}`, {
            method: 'DELETE',
        });
        if (!response.ok) {
            console.error(`Failed to delete job with ID ${jobId}`);
        }
    }
};
