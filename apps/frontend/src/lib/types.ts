export interface CompanyData {
  id: number
  name: string
  website?: string
  logo_url?: string
  industry?: string
}

export interface LocationData {
  city?: string
  state?: string
  country?: string
}

export interface SkillData {
  id: number
  name: string
  label: string
  logo_url?: string
}

export interface JobData {
  id: number
  title: string
  company?: CompanyData
  location?: LocationData
  status: string
  position?: string
  category?: string
  salary_range?: string
  work_model?: string
  required_skills?: SkillData[]
  description?: string
  years_of_experience?: { min?: number; max?: number }
  source_url?: string
  source_platform?: string
  applied_date?: string
  notes?: string
  created_at?: string
  updated_at?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}

export interface JobCreatePayload {
  title: string
  company_id?: number
  company_name?: string
  location?: string
  status?: string
  position?: string
  category?: string
  salary_range?: string
  work_model?: string
  required_skills?: string[]
  description?: string
  source_url?: string
  source_platform?: string
  applied_date?: string
  notes?: string
}

export type JobUpdatePayload = Partial<JobCreatePayload>
