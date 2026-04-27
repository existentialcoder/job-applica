export interface ResumeData {
  id: number
  original_name: string
  file_size: number | null
  url: string
  created_at: string
}

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

export interface StageData {
  key: string
  label: string
  color: string
}

export interface BoardData {
  id: number
  name: string
  color?: string
  description?: string
  stages: StageData[]
  is_default: boolean
  created_at?: string
  updated_at?: string
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
  board_id?: number
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
  board_id?: number
  required_skills?: string[]
  description?: string
  source_url?: string
  source_platform?: string
  applied_date?: string
  notes?: string
}

export type JobUpdatePayload = Partial<JobCreatePayload>

// ── Dashboard ──────────────────────────────────────────────────────────────

export interface DashboardOverview {
  total_saved: number
  total_applied: number
  total_interviews: number
  total_offers: number
  total_rejected: number
  total_withdrawn: number
  total_ghosted: number
  total_stuck: number
  total_active: number
  response_rate: number
  interview_rate: number
  offer_rate: number
}

export interface DashboardStageInfo { key: string; label: string; color: string }
export interface StageCount  { stage: string;    count: number }
export interface WeekCount   { week: string;     count: number }
export interface PlatformCount { platform: string; count: number }
export interface CompanyCount  { company: string;  count: number }

export interface DashboardStats {
  stages: DashboardStageInfo[]
  overview: DashboardOverview
  by_stage: StageCount[]
  by_week: WeekCount[]
  by_platform: PlatformCount[]
  top_companies: CompanyCount[]
}
