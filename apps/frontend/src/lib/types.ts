export interface JobData {
    job_id: string,
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
