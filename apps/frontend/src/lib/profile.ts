export interface ExperienceEntry {
  title: string
  company: string | null
  company_website?: string | null
  start: string | null
  end: string | null
  highlights: string[]
  work_model?: string | null
  job_type?: string | null
  seniority?: string | null
}

export interface EducationEntry {
  institution: string
  degree: string | null
  field: string | null
  start: string | null
  end: string | null
}

export interface Language {
  name: string
  level: string | null
}

export interface ContactDetails {
  email: string | null
  secondary_email: string | null
  phone: string | null
  linkedin_url: string | null
  github_url: string | null
  portfolio_url: string | null
  city: string | null
  country: string | null
}

export interface ProfileFields {
  headline: string | null
  current_title: string | null
  current_company: string | null
  years_experience: number | null
  summary: string | null
  experience: ExperienceEntry[]
  education: EducationEntry[]
  languages: Language[]
  certifications: { name: string; issuer: string | null; year: number | null }[]
  awards: { title: string; issuer: string | null; year: number | null }[]
}

export interface Profile extends ProfileFields {
  contacts: ContactDetails
  auto_filled: string[]
  company_logos: Record<string, string | null>
  source_resume_name: string | null
  confirmed_at: string | null
}

export function emptyProfile(): Profile {
  return {
    headline: null,
    current_title: null,
    current_company: null,
    years_experience: null,
    summary: null,
    experience: [],
    education: [],
    languages: [],
    certifications: [],
    awards: [],
    contacts: {
      email: null,
      secondary_email: null,
      phone: null,
      linkedin_url: null,
      github_url: null,
      portfolio_url: null,
      city: null,
      country: null
    },
    auto_filled: [],
    company_logos: {},
    source_resume_name: null,
    confirmed_at: null
  };
}

export interface JobPreferences {
  target_titles: string[]
  locations: { city: string | null; country: string | null }[]
  work_models: string[]
  seniority: string[]
  job_types: string[]
  salary_min: number | null
  salary_currency: string | null
  salary_period: 'year' | 'month' | 'hour' | null
  notice_period_days: number | null
  open_to_relocation: boolean
  needs_visa_sponsorship: boolean
}
