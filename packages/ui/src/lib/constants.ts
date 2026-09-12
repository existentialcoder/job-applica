export const DEFAULT_COMPANY_LOGO_URL =
  "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%239ca3af' stroke-width='1.5'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' d='M3 21h18M6 21V7a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v14M15 21v-9a1 1 0 0 1 1-1h3a1 1 0 0 1 1 1v9M9 9h1M9 12h1M9 15h1'/%3E%3C/svg%3E"

export interface StageData {
  key: string
  label: string
  color: string
}

export interface ColorOption {
  value: string
  label: string
}

export const COLOR_PALETTE: ColorOption[] = [
  { value: 'bg-slate-500', label: 'Slate' },
  { value: 'bg-blue-500', label: 'Blue' },
  { value: 'bg-violet-500', label: 'Violet' },
  { value: 'bg-emerald-500', label: 'Emerald' },
  { value: 'bg-amber-500', label: 'Amber' },
  { value: 'bg-rose-500', label: 'Rose' },
  { value: 'bg-orange-500', label: 'Orange' },
  { value: 'bg-cyan-500', label: 'Cyan' },
  { value: 'bg-pink-500', label: 'Pink' },
  { value: 'bg-teal-500', label: 'Teal' },
  { value: 'bg-indigo-500', label: 'Indigo' },
  { value: 'bg-zinc-400', label: 'Zinc' }
];

export const DEFAULT_BOARD_STAGES: StageData[] = [
  { key: 'Saved', label: 'Saved', color: 'bg-slate-500' },
  { key: 'Applied', label: 'Applied', color: 'bg-blue-500' },
  { key: 'Phone Screen', label: 'Phone Screen', color: 'bg-amber-500' },
  { key: 'Interview', label: 'Interview', color: 'bg-amber-500' },
  { key: 'Offer', label: 'Offer', color: 'bg-emerald-500' },
  { key: 'Accepted', label: 'Accepted', color: 'bg-teal-500' },
  { key: 'Rejected', label: 'Rejected', color: 'bg-rose-500' },
  { key: 'Withdrawn', label: 'Withdrawn', color: 'bg-zinc-400' },
  { key: 'Ghosted', label: 'Ghosted', color: 'bg-rose-500' },
  { key: 'Archived', label: 'Archived', color: 'bg-zinc-400' }
];
