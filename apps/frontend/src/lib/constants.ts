// Inline SVG (generic building glyph) — the previous fallback (a DuckDuckGo icon-proxy
// URL) 404s unconditionally since "default" isn't a real domain, silently hiding the
// logo for every company without its own stored logo_url. This one never 404s.
export const DEFAULT_COMPANY_LOGO_URL =
  "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%239ca3af' stroke-width='1.5'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' d='M3 21h18M6 21V7a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v14M15 21v-9a1 1 0 0 1 1-1h3a1 1 0 0 1 1 1v9M9 9h1M9 12h1M9 15h1'/%3E%3C/svg%3E"

export const DEFAULT_BOARD_STAGES = [
  { key: 'Saved', label: 'Saved', color: 'bg-slate-500' },
  { key: 'Applied', label: 'Applied', color: 'bg-blue-500' },
  { key: 'Phone Screen', label: 'Phone Screen', color: 'bg-amber-500' },
  { key: 'Interview', label: 'Interview', color: 'bg-amber-500' },
  { key: 'Offer', label: 'Offer', color: 'bg-emerald-500' },
  { key: 'Accepted', label: 'Accepted', color: 'bg-emerald-600' },
  { key: 'Rejected', label: 'Rejected', color: 'bg-red-500' },
  { key: 'Withdrawn', label: 'Withdrawn', color: 'bg-zinc-400' },
  { key: 'Ghosted', label: 'Ghosted', color: 'bg-purple-400' },
  { key: 'Archived', label: 'Archived', color: 'bg-zinc-300' }
]

export const MANDATORY_STAGE_KEYS: string[] = DEFAULT_BOARD_STAGES.map((s) => s.key)

export const POSITION_OPTIONS = ['Intern', 'Junior', 'Mid', 'Senior', 'Lead', 'Manager']
export const WORK_MODEL_OPTIONS = ['On-site', 'Remote', 'Hybrid']

export interface AtsTier {
  key: string
  label: string
  min: number
  max: number
  badgeClass: string
  color: string
  // Selected-chip look only — unselected chips stay the plain default outline style.
  // Kept as a fully literal string (not built via template interpolation) since
  // Tailwind's JIT scanner only picks up class names it can see statically in source.
  chipActiveClass: string
}

// Single source of truth for ATS score tiers — used for the score badge/gauge display
// (JobDetailPanel.vue) and the tier-chip filter (JobFiltersPanel.vue), so the two can't
// silently drift apart the way atsScoreColor/atsTierLabel previously did.
export const ATS_SCORE_TIERS: AtsTier[] = [
  {
    key: 'low',
    label: 'Low',
    min: 0,
    max: 50,
    color: '#ef4444',
    badgeClass: 'bg-red-500/10 text-red-400',
    chipActiveClass: 'border-red-500 text-red-500 bg-red-500/10'
  },
  {
    key: 'good',
    label: 'Good',
    min: 50,
    max: 85,
    color: '#f97316',
    badgeClass: 'bg-orange-500/10 text-orange-500',
    chipActiveClass: 'border-orange-500 text-orange-500 bg-orange-500/10'
  },
  {
    key: 'excellent',
    label: 'Excellent',
    min: 85,
    max: 100,
    color: '#22c55e',
    badgeClass: 'bg-green-500/10 text-green-500',
    chipActiveClass: 'border-green-500 text-green-500 bg-green-500/10'
  }
]

export function getAtsTier(score: number): AtsTier {
  for (let i = ATS_SCORE_TIERS.length - 1; i >= 0; i--) {
    if (score >= ATS_SCORE_TIERS[i].min) return ATS_SCORE_TIERS[i]
  }
  return ATS_SCORE_TIERS[0]
}

// Multi-select tiers map to ONE contiguous ats_score_min/max range on the backend (it
// doesn't support OR-ing multiple disjoint ranges). For adjacent selections (e.g.
// Good+Excellent) this is exact. For a non-adjacent selection (Low+Excellent without
// Good) it widens to the full span and also matches Good-range jobs — a known
// limitation given the current single-range backend filter.
export function atsTiersFilterRange(tierKeys: string[]): { min: number; max: number } | null {
  const selected = ATS_SCORE_TIERS.filter((t) => tierKeys.includes(t.key))
  if (!selected.length) return null
  const topTier = ATS_SCORE_TIERS[ATS_SCORE_TIERS.length - 1]
  const max = Math.max(...selected.map((t) => t.max))
  return {
    min: Math.min(...selected.map((t) => t.min)),
    max: selected.some((t) => t === topTier) ? max : max - 0.01
  }
}

export const COUNTRY_OPTIONS = [
  'Afghanistan',
  'Albania',
  'Algeria',
  'Andorra',
  'Angola',
  'Argentina',
  'Armenia',
  'Australia',
  'Austria',
  'Azerbaijan',
  'Bahamas',
  'Bahrain',
  'Bangladesh',
  'Barbados',
  'Belarus',
  'Belgium',
  'Belize',
  'Benin',
  'Bhutan',
  'Bolivia',
  'Bosnia and Herzegovina',
  'Botswana',
  'Brazil',
  'Brunei',
  'Bulgaria',
  'Burkina Faso',
  'Burundi',
  'Cambodia',
  'Cameroon',
  'Canada',
  'Cape Verde',
  'Central African Republic',
  'Chad',
  'Chile',
  'China',
  'Colombia',
  'Comoros',
  'Costa Rica',
  'Croatia',
  'Cuba',
  'Cyprus',
  'Czech Republic',
  'Denmark',
  'Djibouti',
  'Dominica',
  'Dominican Republic',
  'Ecuador',
  'Egypt',
  'El Salvador',
  'Equatorial Guinea',
  'Eritrea',
  'Estonia',
  'Eswatini',
  'Ethiopia',
  'Fiji',
  'Finland',
  'France',
  'Gabon',
  'Gambia',
  'Georgia',
  'Germany',
  'Ghana',
  'Greece',
  'Grenada',
  'Guatemala',
  'Guinea',
  'Guinea-Bissau',
  'Guyana',
  'Haiti',
  'Honduras',
  'Hungary',
  'Iceland',
  'India',
  'Indonesia',
  'Iran',
  'Iraq',
  'Ireland',
  'Israel',
  'Italy',
  'Jamaica',
  'Japan',
  'Jordan',
  'Kazakhstan',
  'Kenya',
  'Kiribati',
  'Kuwait',
  'Kyrgyzstan',
  'Laos',
  'Latvia',
  'Lebanon',
  'Lesotho',
  'Liberia',
  'Libya',
  'Liechtenstein',
  'Lithuania',
  'Luxembourg',
  'Madagascar',
  'Malawi',
  'Malaysia',
  'Maldives',
  'Mali',
  'Malta',
  'Marshall Islands',
  'Mauritania',
  'Mauritius',
  'Mexico',
  'Micronesia',
  'Moldova',
  'Monaco',
  'Mongolia',
  'Montenegro',
  'Morocco',
  'Mozambique',
  'Myanmar',
  'Namibia',
  'Nauru',
  'Nepal',
  'Netherlands',
  'New Zealand',
  'Nicaragua',
  'Niger',
  'Nigeria',
  'North Korea',
  'North Macedonia',
  'Norway',
  'Oman',
  'Pakistan',
  'Palau',
  'Panama',
  'Papua New Guinea',
  'Paraguay',
  'Peru',
  'Philippines',
  'Poland',
  'Portugal',
  'Qatar',
  'Romania',
  'Russia',
  'Rwanda',
  'Saint Lucia',
  'Samoa',
  'San Marino',
  'Saudi Arabia',
  'Senegal',
  'Serbia',
  'Seychelles',
  'Sierra Leone',
  'Singapore',
  'Slovakia',
  'Slovenia',
  'Solomon Islands',
  'Somalia',
  'South Africa',
  'South Korea',
  'South Sudan',
  'Spain',
  'Sri Lanka',
  'Sudan',
  'Suriname',
  'Sweden',
  'Switzerland',
  'Syria',
  'Taiwan',
  'Tajikistan',
  'Tanzania',
  'Thailand',
  'Timor-Leste',
  'Togo',
  'Tonga',
  'Trinidad and Tobago',
  'Tunisia',
  'Turkey',
  'Turkmenistan',
  'Tuvalu',
  'Uganda',
  'Ukraine',
  'United Arab Emirates',
  'United Kingdom',
  'United States',
  'Uruguay',
  'Uzbekistan',
  'Vanuatu',
  'Vatican City',
  'Venezuela',
  'Vietnam',
  'Yemen',
  'Zambia',
  'Zimbabwe'
]
