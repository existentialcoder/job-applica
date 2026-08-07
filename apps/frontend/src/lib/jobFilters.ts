export type DateRangePreset = '7d' | '14d' | '30d' | 'custom' | ''

export interface DateRange {
  from: string
  to: string
}

export interface JobFiltersFormValues {
  boardIds: string[]
  status: string[]
  city: string
  country: string[]
  company: string[]
  workModel: string[]
  position: string[]
  appliedPreset: DateRangePreset
  appliedRange: DateRange
  createdPreset: DateRangePreset
  createdRange: DateRange
  atsScoreTiers: string[]
}

export function emptyJobFilters(): JobFiltersFormValues {
  return {
    boardIds: [],
    status: [],
    city: '',
    country: [],
    company: [],
    workModel: [],
    position: [],
    appliedPreset: '',
    appliedRange: { from: '', to: '' },
    createdPreset: '',
    createdRange: { from: '', to: '' },
    atsScoreTiers: []
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
