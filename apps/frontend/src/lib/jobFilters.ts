export type DateRangePreset = '7d' | '14d' | '30d' | 'custom' | ''

export interface JobFiltersFormValues {
  boardIds: string[]
  status: string[]
  location: string
  country: string[]
  company: string
  workModel: string[]
  position: string[]
  appliedPreset: DateRangePreset
  appliedFrom: string
  appliedTo: string
  createdPreset: DateRangePreset
  createdFrom: string
  createdTo: string
  atsScoreMin: string
  atsScoreMax: string
}

export function emptyJobFilters(): JobFiltersFormValues {
  return {
    boardIds: [],
    status: [],
    location: '',
    country: [],
    company: '',
    workModel: [],
    position: [],
    appliedPreset: '',
    appliedFrom: '',
    appliedTo: '',
    createdPreset: '',
    createdFrom: '',
    createdTo: '',
    atsScoreMin: '',
    atsScoreMax: ''
  }
}

const PRESET_DAYS: Record<'7d' | '14d' | '30d', number> = {
  '7d': 7,
  '14d': 14,
  '30d': 30
}

export function resolvePresetRange(preset: DateRangePreset): { from: string; to: string } | null {
  if (preset !== '7d' && preset !== '14d' && preset !== '30d') return null
  const to = new Date()
  const from = new Date(to)
  from.setDate(from.getDate() - PRESET_DAYS[preset])
  return { from: from.toISOString().slice(0, 10), to: to.toISOString().slice(0, 10) }
}
