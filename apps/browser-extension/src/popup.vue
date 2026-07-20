<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue';
import dataservice, { type BoardData, type JobExtractResult, type CompanyResult, type ATSReport, type ExtractedLocation } from './lib/dataservice';
import ext from './lib/ext';
import { config, loadConfig, saveConfig, resetConfig } from './lib/config';
import { Button } from '@job-applica/ui/components/ui/button';
import { Input } from '@job-applica/ui/components/ui/input';
import { Label } from '@job-applica/ui/components/ui/label';
import { Badge } from '@job-applica/ui/components/ui/badge';
import { NativeSelect } from '@job-applica/ui/components/ui/select';
import { Textarea } from '@job-applica/ui/components/ui/textarea';
import { THEME_ACCENTS } from '@job-applica/ui/theme';

function formatLocation(loc: JobExtractResult['location']): string {
  if (!loc) return '';
  return [loc.city, loc.state, loc.country].filter(Boolean).join(', ');
}

function parseLocationString(loc: string): ExtractedLocation | undefined {
  if (!loc.trim()) return undefined;
  const [city, state, country] = loc.split(',').map(p => p.trim());
  return { city: city || null, state: state || null, country: country || null };
}

// ── Theme ─────────────────────────────────────────────────────────────────────
const isDark = ref(false);

function applyTheme(dark: boolean, themeKey: string) {
  isDark.value = dark;
  document.documentElement.classList.toggle('dark', dark);
  const t = THEME_ACCENTS[themeKey] ?? (dark ? THEME_ACCENTS.noir : THEME_ACCENTS.white);
  document.documentElement.style.setProperty('--primary', t.accent);
  document.documentElement.style.setProperty('--primary-foreground', t.accentFg);
  document.documentElement.style.setProperty('--ring', t.accent);
}

async function getThemeKey(dark: boolean): Promise<string> {
  try {
    const settings = await dataservice.getSettings();
    return dark
      ? ((settings.dark_bg_theme as string) || 'noir')
      : ((settings.light_bg_theme as string) || 'white');
  } catch {
    return dark ? 'noir' : 'white';
  }
}

async function initDarkMode() {
  // Apply cached dark_mode immediately so the popup isn't unstyled while loading
  const cached = await ext.storage.local.get(['dark_mode']);
  const darkCached = typeof cached.dark_mode === 'boolean' ? cached.dark_mode : false;
  applyTheme(darkCached, darkCached ? 'noir' : 'white');

  try {
    const settings = await dataservice.getSettings();
    const themeVal = settings.theme as string | undefined;
    const isDarkMode = themeVal === 'dark' || (themeVal === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches);
    const lightKey = (settings.light_bg_theme as string) || 'white';
    const darkKey  = (settings.dark_bg_theme  as string) || 'noir';
    applyTheme(isDarkMode, isDarkMode ? darkKey : lightKey);
    ext.storage.local.set({ dark_mode: isDarkMode });
  } catch { /* offline — keep cached dark_mode */ }
}

async function toggleDark() {
  const next = !isDark.value;
  const key = await getThemeKey(next);
  applyTheme(next, key);
  ext.storage.local.set({ dark_mode: next });
  await dataservice.updateSettings({ theme: next ? 'dark' : 'light' });
}

// ── View state ──────────────────────────────────────────────────────────────
const view = ref<'loading' | 'login' | 'setup' | 'job' | 'no-job' | 'settings'>('loading');
let preSettingsView: typeof view.value = 'no-job';

// ── Settings ─────────────────────────────────────────────────────────────────
const settingsApiUrl = ref('');
const settingsAppUrl = ref('');
const settingsSaved = ref(false);

function openSettings() {
  preSettingsView = view.value;
  settingsApiUrl.value = config.apiBase;
  settingsAppUrl.value = config.appUrl;
  settingsSaved.value = false;
  view.value = 'settings';
}

function closeSettings() {
  view.value = preSettingsView;
}


async function handleSaveSettings() {
  const api = settingsApiUrl.value.trim();
  const app = settingsAppUrl.value.trim();
  if (!api || !app) return;
  await saveConfig(api, app);
  settingsSaved.value = true;
  setTimeout(() => { settingsSaved.value = false; }, 2000);
}

async function handleResetSettings() {
  await resetConfig();
  settingsApiUrl.value = config.apiBase;
  settingsAppUrl.value = config.appUrl;
  settingsSaved.value = false;
}

// ── Auth ─────────────────────────────────────────────────────────────────────
const loginUsername = ref('');
const loginPassword = ref('');
const loginError = ref('');
const isLoginLoading = ref(false);
const isOAuthLoading = ref<'google' | 'linkedin' | null>(null);

async function handleLogin() {
  loginError.value = '';
  isLoginLoading.value = true;
  const ok = await dataservice.login(loginUsername.value, loginPassword.value);
  isLoginLoading.value = false;
  if (ok) {
    await setupData();
  } else {
    loginError.value = 'Invalid credentials. Please try again.';
  }
}

function openOAuth(provider: 'google' | 'linkedin') {
  isOAuthLoading.value = provider;
  ext.tabs.create({ url: `${config.apiBase}/auth/${provider}?origin=extension` });
}

async function handleLogout() {
  await dataservice.logout();
  view.value = 'login';
}

// ── First-run board setup ─────────────────────────────────────────────────────
const newBoardName = ref('My Job Search');
const isCreatingBoard = ref(false);
const createBoardError = ref('');

async function handleCreateBoard() {
  if (!newBoardName.value.trim()) return;
  isCreatingBoard.value = true;
  createBoardError.value = '';
  const board = await dataservice.createBoard(newBoardName.value.trim());
  isCreatingBoard.value = false;
  if (!board) {
    createBoardError.value = 'Could not create board. Please try again.';
    return;
  }
  boards.value = [board];
  selectedBoardId.value = board.id;
  await ext.storage.local.set({ last_board_id: board.id });
  const url = await dataservice.getCurrentTabUrl();
  currentUrl.value = url;
  view.value = url && dataservice.isJobPage(url) ? 'job' : 'no-job';
}

// ── Job data ──────────────────────────────────────────────────────────────────
const platform = ref<string | null>(null);
const currentUrl = ref<string | null>(null);
const jobTitle = ref('');
const company = ref<CompanyResult>({ name: '', website: '', email: '', size: null, industry: '', description: '', logo_url: '' });
const jobLocation = ref('');
const structuredLocation = ref<ExtractedLocation | null>(null);
const jobDescription = ref<string | null>(null);
const salaryRange = ref<string | null>(null);
const workModel = ref('On-site');
const jobStatus = ref('Saved');
const notes = ref('');
const existingJobId = ref<number | null>(null);
const isSaveBtnLoading = ref(false);
const saveError = ref('');
const isFetchingData = ref(false);
const atsReport = ref<ATSReport | null>(null);
const isLoadingAts = ref(false);
const noResume = ref(false);
const extractedRequiredSkills = ref<string[]>([]);

// ── Boards ────────────────────────────────────────────────────────────────────
const boards = ref<BoardData[]>([]);
const selectedBoardId = ref<number | null>(null);

const selectedBoard = computed(() =>
  boards.value.find(b => b.id === selectedBoardId.value) ?? null
);

const statusOptions = computed<string[]>(() => {
  const stages = selectedBoard.value?.stages;
  return stages?.length ? stages.map((s) => s.key) : ['Saved', 'Applied', 'Phone Screen', 'Interview', 'Technical', 'Offer', 'Rejected', 'Withdrawn'];
});

watch(selectedBoardId, async (id: number | null) => {
  if (id !== null) {
    await ext.storage.local.set({ last_board_id: id });
    // Re-fetch to get the latest stages (user may have edited them in the web app)
    const fresh = await dataservice.getBoard(id);
    if (fresh) {
      const idx = boards.value.findIndex(b => b.id === id);
      if (idx !== -1) boards.value[idx] = fresh;
      else boards.value.push(fresh);
    }
    const stages = selectedBoard.value?.stages;
    jobStatus.value = stages?.[0]?.key ?? 'Saved';
  }
});

watch(statusOptions, (opts: string[]) => {
  if (!opts.includes(jobStatus.value)) {
    jobStatus.value = opts[0] ?? 'Saved';
  }
}, { immediate: true });

let setupInProgress = false;

async function setupData() {
  if (setupInProgress) {
    return;
  }
  setupInProgress = true;
  try {
    await _setupData();
  } finally {
    setupInProgress = false;
  }
}

async function _setupData() {
  let loggedIn = await dataservice.isLoggedIn();
  if (!loggedIn) {
    // Try to pull the session from any open web app tab before showing login
    loggedIn = await dataservice.syncFromWebApp();
  }
  if (!loggedIn) {
    view.value = 'login';
    return;
  }

  const url = await dataservice.getCurrentTabUrl();
  currentUrl.value = url;
  if (!url) { 
    view.value = 'no-job';
    return;
  }

  platform.value = dataservice.detectPlatform(url);

  // Load boards in parallel with page text extraction
  const [fetchedBoards, cached, tabs] = await Promise.all([
    dataservice.getBoards(),
    ext.storage.local.get(['last_board_id']),
    ext.tabs.query({ active: true, currentWindow: true }),
  ]);
  boards.value = fetchedBoards;

  if (fetchedBoards.length === 0) {
    view.value = 'setup';
    return;
  }

  const lastId = cached.last_board_id as number | undefined;
  const defaultBoard = fetchedBoards.find((b: BoardData) => b.is_default);
  selectedBoardId.value = fetchedBoards.find((b: BoardData) => b.id === lastId)?.id ?? defaultBoard?.id ?? fetchedBoards[0]?.id ?? null;

  const tabId = tabs[0]?.id;
  const tabUrl = tabs[0]?.url || null;
  if (!tabId) {
    view.value = 'no-job';
    return;
  }

  view.value = 'job';
  isFetchingData.value = true;

  try {
    // Check if URL is already saved AND browser cache simultaneously
    const [savedId, pageCache] = await Promise.all([
      tabUrl ? dataservice.checkJobExistsByUrl(tabUrl) : Promise.resolve(null),
      tabUrl ? dataservice.getCachedPage(tabUrl) : Promise.resolve(null),
    ]);

    if (savedId !== null) {
      existingJobId.value = savedId;
      return;
    }

    if (pageCache) {
      const { extraction, atsReport: cachedAts, noResume: cachedNoResume } = pageCache;
      if (extraction.title) jobTitle.value = extraction.title;
      if (extraction.company) company.value = extraction.company;
      if (extraction.location) { jobLocation.value = formatLocation(extraction.location); structuredLocation.value = extraction.location; }
      if (extraction.description) jobDescription.value = extraction.description;
      if (extraction.salary_range) salaryRange.value = extraction.salary_range;
      if (extraction.work_model) workModel.value = extraction.work_model;
      extractedRequiredSkills.value = extraction.required_skills ?? [];
      atsReport.value = cachedAts;
      noResume.value = cachedNoResume;
      return;
    }

    // Fresh extraction via LLM
    const [scriptResult] = await ext.scripting.executeScript({
      target: { tabId },
      func: () => {
        const clone = document.body.cloneNode(true) as Element;
        clone.querySelectorAll('script, style, noscript, svg').forEach(el => el.remove());
        const pageText = (clone.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 15000);
        return { pageText, href: window.location.href };
      },
    });

    const extracted: JobExtractResult | null = scriptResult?.result?.pageText
      ? await dataservice.extractJobFromPage(scriptResult.result.pageText, scriptResult.result.href)
      : null;

    if (!extracted?.is_job_page) {
      view.value = 'no-job';
    } else {
      if (extracted.title) jobTitle.value = extracted.title;
      if (extracted.company) company.value = extracted.company;
      if (extracted.location) { jobLocation.value = formatLocation(extracted.location); structuredLocation.value = extracted.location; }
      if (extracted.description) jobDescription.value = extracted.description;
      if (extracted.salary_range) salaryRange.value = extracted.salary_range;
      if (extracted.work_model) workModel.value = extracted.work_model;
      extractedRequiredSkills.value = extracted.required_skills ?? [];

      // Fallback duplicate check by title+company
      if (jobTitle.value) {
        existingJobId.value = await dataservice.checkJobExists(jobTitle.value, company.value.name || undefined);
      }

      // ATS scoring in background — same prompt/endpoint as dashboard (required_skills hint included)
      if (extracted.description && !existingJobId.value) {
        isLoadingAts.value = true;
        atsReport.value = null;
        noResume.value = false;
        dataservice.quickAtsScore(extracted.description, extracted.required_skills ?? []).then(result => {
          const isNoResume = result === 'no_resume';
          const report = isNoResume ? null : result;
          atsReport.value = report;
          noResume.value = isNoResume;
          isLoadingAts.value = false;
          // Cache extraction + ATS so next popup open is instant
          if (tabUrl) {
            dataservice.setCachedPage(tabUrl, { 
              extraction: extracted,
              atsReport: report,
              noResume: isNoResume
            });
          }
        });
      }
    }
  } catch {
    view.value = 'no-job';
  } finally {
    isFetchingData.value = false;
  }
}

// Listen for storage changes written by background.js (OAuth)
function onStorageChange(changes: Record<string, { newValue?: any; oldValue?: any }>) {
  if (changes.access_token?.newValue) {
    isOAuthLoading.value = null;
    setupData();
  }
}

onMounted(async () => {
  await loadConfig();
  await initDarkMode();
  ext.storage.onChanged.addListener(onStorageChange);
  await setupData();
});

onUnmounted(() => {
  ext.storage.onChanged.removeListener(onStorageChange);
});

async function retryFetch() {
  jobTitle.value = '';
  company.value = {} as CompanyResult;
  jobLocation.value = '';
  structuredLocation.value = null;
  jobDescription.value = null;
  salaryRange.value = null;
  atsReport.value = null;
  isLoadingAts.value = false;
  noResume.value = false;
  extractedRequiredSkills.value = [];
  if (currentUrl.value) await dataservice.clearCachedPage(currentUrl.value);
  isFetchingData.value = true;

  try {
    const tabs = await ext.tabs.query({ active: true, currentWindow: true });
    const tabId = tabs[0]?.id;
    if (!tabId) return;

    const [scriptResult] = await ext.scripting.executeScript({
      target: { tabId },
      func: () => {
        const clone = document.body.cloneNode(true) as Element;
        clone.querySelectorAll('script, style, noscript, svg').forEach(el => el.remove());
        const pageText = (clone.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 15000);
        return { pageText, href: window.location.href };
      },
    });

    const extracted: JobExtractResult | null = scriptResult?.result?.pageText
      ? await dataservice.extractJobFromPage(scriptResult.result.pageText, scriptResult.result.href)
      : null;

    if (extracted?.is_job_page) {
      if (extracted.title) jobTitle.value = extracted.title;
      if (extracted.company) company.value = extracted.company;
      if (extracted.location) { jobLocation.value = formatLocation(extracted.location); structuredLocation.value = extracted.location; }
      if (extracted.description) jobDescription.value = extracted.description;
      if (extracted.salary_range) salaryRange.value = extracted.salary_range;
      if (extracted.work_model) workModel.value = extracted.work_model;
      extractedRequiredSkills.value = extracted.required_skills ?? [];

      if (extracted.description) {
        isLoadingAts.value = true;
        dataservice.quickAtsScore(extracted.description, extracted.required_skills ?? []).then(result => {
          const isNoResume = result === 'no_resume';
          const report = isNoResume ? null : result;
          atsReport.value = report;
          noResume.value = isNoResume;
          isLoadingAts.value = false;
          if (currentUrl.value) {
            dataservice.setCachedPage(currentUrl.value, { extraction: extracted, atsReport: report, noResume: isNoResume });
          }
        });
      }
    }
  } finally {
    isFetchingData.value = false;
  }
}

async function saveJob() {
  isSaveBtnLoading.value = true;
  saveError.value = '';

  try {
    const report = atsReport.value;
    const jobId = await dataservice.createJob({
      title: jobTitle.value,
      company: company.value || undefined,
      location: structuredLocation.value ?? parseLocationString(jobLocation.value),
      status: jobStatus.value,
      salary_range: salaryRange.value || undefined,
      description: jobDescription.value?.trim() || undefined,
      work_model: workModel.value,
      source_url: currentUrl.value || undefined,
      source_platform: platform.value || undefined,
      notes: notes.value || undefined,
      board_id: selectedBoardId.value ?? undefined,
      required_skills: extractedRequiredSkills.value,
      ats_score: report?.score ?? undefined,
      ats_report: report
        ? { score: report.score, matched_skills: report.matched_skills, missing_skills: report.missing_skills, suggestions: report.suggestions, resume_id: report.resume_id }
        : undefined,
      ats_resume_id: report?.resume_id ?? undefined,
    });

    if (jobId !== null) {
      existingJobId.value = jobId;
      if (currentUrl.value) dataservice.clearCachedPage(currentUrl.value);
    } else {
      saveError.value = 'Failed to save. Please try again.';
    }
  } finally {
    isSaveBtnLoading.value = false;
  }
}

const atsScoreColor = computed(() => {
  const s = atsReport.value?.score ?? 0;
  if (s >= 75) return 'text-green-600 dark:text-green-400';
  if (s >= 50) return 'text-yellow-600 dark:text-yellow-400';
  return 'text-red-500 dark:text-red-400';
});

const atsGaugeStroke = computed(() => {
  const s = atsReport.value?.score ?? 0;
  if (s >= 75) return '#22c55e';
  if (s >= 50) return '#f59e0b';
  return '#ef4444';
});

const platformBadgeVariant: Record<string, any> = {
  LinkedIn: 'default',
  Indeed: 'default',
  Glassdoor: 'success',
  Monster: 'warning',
  ZipRecruiter: 'success',
  Jobscan: 'warning',
};
</script>

<template>
  <div class="popup-container w-full bg-background text-foreground flex flex-col">
    <!-- Header -->
    <div class="flex items-center justify-between px-4 py-3 border-b border-border">
      <div class="flex items-center gap-2">
        <svg width="22" height="22" viewBox="20 0 432 480" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
          <defs>
            <linearGradient id="popup-dew" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="#4F46E5"/>
              <stop offset="100%" stop-color="#7C3AED"/>
            </linearGradient>
          </defs>
          <path fill="url(#popup-dew)" d="M 430,112 C 452,222 362,470 230,470 A 200,200 0 0 1 30,270 C 30,78 172,8 430,112 Z"/>
          <circle cx="248" cy="154" r="22" fill="white"/>
          <path fill="white" d="M 231,194 L 265,194 L 265,360 Q 265,442 210,442 Q 172,442 172,406 L 172,388 Q 172,418 210,418 Q 248,418 248,360 L 248,194 Z"/>
        </svg>
        <span class="text-sm font-bold">Job<span class="text-indigo-400">Applica</span></span>
      </div>
      <div class="flex items-center gap-2">
        <Badge v-if="platform" :variant="platformBadgeVariant[platform] || 'secondary'" class="text-xs">
          {{ platform }}
        </Badge>
        <button v-if="view !== 'login'" @click="handleLogout"
          class="text-xs text-muted-foreground hover:text-destructive transition">
          Sign out
        </button>
        <!-- Settings -->
        <button @click="view === 'settings' ? closeSettings() : openSettings()"
          class="p-1 rounded text-muted-foreground hover:text-foreground hover:bg-muted transition"
          title="Settings">
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="3"/>
            <path stroke-linecap="round" d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z"/>
          </svg>
        </button>
        <!-- Dark mode toggle -->
        <button @click="toggleDark"
          class="p-1 rounded text-muted-foreground hover:text-foreground hover:bg-muted transition"
          :title="isDark ? 'Switch to light mode' : 'Switch to dark mode'">
          <!-- Sun icon (shown in dark mode) -->
          <svg v-if="isDark" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="5"/>
            <path stroke-linecap="round" d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>
          </svg>
          <!-- Moon icon (shown in light mode) -->
          <svg v-else class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"/>
          </svg>
        </button>
      </div>
    </div>

    <!-- Settings view -->
    <div v-if="view === 'settings'" class="p-4 flex flex-col gap-4">
      <div class="flex items-center gap-2">
        <button @click="closeSettings" class="p-1 rounded text-muted-foreground hover:text-foreground hover:bg-muted transition" title="Back">
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7"/>
          </svg>
        </button>
        <span class="text-sm font-semibold">Settings</span>
      </div>

      <div class="rounded-md border border-border bg-muted/40 p-3 text-xs text-muted-foreground">
        Override these values on a self-hosted JobApplica version.
      </div>

      <div class="flex flex-col gap-1.5">
        <Label for="settings-app-url">App URL</Label>
        <Input id="settings-app-url" v-model="settingsAppUrl" placeholder="https://app.jobapplica.io" class="text-xs font-mono" />
      </div>

      <div class="flex flex-col gap-1.5">
        <Label for="settings-api-url">API URL</Label>
        <Input id="settings-api-url" v-model="settingsApiUrl" placeholder="https://api.jobapplica.io/api/v1" class="text-xs font-mono" />
      </div>

      <div class="flex gap-2">
        <Button class="flex-1" @click="handleSaveSettings">
          {{ settingsSaved ? '✓ Saved' : 'Save' }}
        </Button>
        <Button variant="outline" @click="handleResetSettings" title="Reset to cloud defaults">
          Reset
        </Button>
      </div>
    </div>

    <!-- Initial loading skeleton (shown while setupData runs) -->
    <div v-else-if="view === 'loading'" class="p-4 flex flex-col gap-3">
      <div class="flex flex-col gap-3">
        <div class="flex flex-col gap-1.5">
          <div class="h-3 w-10 rounded bg-muted animate-pulse"></div>
          <div class="h-9 rounded-md bg-muted animate-pulse"></div>
        </div>
        <div class="flex flex-col gap-1.5">
          <div class="h-3 w-14 rounded bg-muted animate-pulse"></div>
          <div class="h-9 rounded-md bg-muted animate-pulse"></div>
        </div>
        <div class="flex flex-col gap-1.5">
          <div class="h-3 w-16 rounded bg-muted animate-pulse"></div>
          <div class="h-9 rounded-md bg-muted animate-pulse"></div>
        </div>
        <div class="flex flex-col gap-1.5">
          <div class="h-3 w-14 rounded bg-muted animate-pulse"></div>
          <div class="h-9 rounded-md bg-muted animate-pulse"></div>
        </div>
        <div class="grid grid-cols-2 gap-2">
          <div class="flex flex-col gap-1.5">
            <div class="h-3 w-10 rounded bg-muted animate-pulse"></div>
            <div class="h-9 rounded-md bg-muted animate-pulse"></div>
          </div>
          <div class="flex flex-col gap-1.5">
            <div class="h-3 w-20 rounded bg-muted animate-pulse"></div>
            <div class="h-9 rounded-md bg-muted animate-pulse"></div>
          </div>
        </div>
        <div class="flex flex-col gap-1.5">
          <div class="h-3 w-9 rounded bg-muted animate-pulse"></div>
          <div class="h-14 rounded-md bg-muted animate-pulse"></div>
        </div>
        <div class="h-9 rounded-md bg-muted animate-pulse"></div>
      </div>
    </div>

    <!-- Login view -->
    <div v-else-if="view === 'login'" class="p-4 flex flex-col gap-3">
      <p class="text-sm text-muted-foreground text-center">Sign in to track jobs</p>

      <!-- OAuth buttons -->
      <Button variant="outline" class="w-full gap-2 justify-center" type="button"
        :disabled="isOAuthLoading !== null" @click="openOAuth('google')">
        <svg v-if="isOAuthLoading === 'google'" class="w-4 h-4 animate-spin" xmlns="http://www.w3.org/2000/svg"
          fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
        </svg>
        <svg v-else class="w-4 h-4 flex-shrink-0" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
          <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
          <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
          <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
        </svg>
        {{ isOAuthLoading === 'google' ? 'Opening…' : 'Continue with Google' }}
      </Button>

      <Button variant="outline" class="w-full gap-2 justify-center" type="button"
        :disabled="isOAuthLoading !== null" @click="openOAuth('linkedin')">
        <svg v-if="isOAuthLoading === 'linkedin'" class="w-4 h-4 animate-spin" xmlns="http://www.w3.org/2000/svg"
          fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
        </svg>
        <svg v-else class="w-4 h-4 flex-shrink-0" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" fill="#0A66C2">
          <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
        </svg>
        {{ isOAuthLoading === 'linkedin' ? 'Opening…' : 'Continue with LinkedIn' }}
      </Button>

      <!-- Divider -->
      <div class="relative my-1">
        <div class="absolute inset-0 flex items-center">
          <div class="w-full border-t border-border"></div>
        </div>
        <div class="relative flex justify-center text-xs">
          <span class="bg-background px-2 text-muted-foreground">or sign in with password</span>
        </div>
      </div>

      <div class="flex flex-col gap-1.5">
        <Label for="login-username">Username or Email</Label>
        <Input id="login-username" v-model="loginUsername" type="text" placeholder="username" />
      </div>
      <div class="flex flex-col gap-1.5">
        <Label for="login-password">Password</Label>
        <Input id="login-password" v-model="loginPassword" type="password" placeholder="••••••••"
          @keyup.enter="handleLogin" />
      </div>
      <p v-if="loginError" class="text-xs text-destructive">{{ loginError }}</p>
      <Button @click="handleLogin" :disabled="isLoginLoading" class="w-full">
        {{ isLoginLoading ? 'Signing in...' : 'Sign In' }}
      </Button>
    </div>

    <!-- First-run setup view -->
    <div v-else-if="view === 'setup'" class="p-4 flex flex-col gap-4">
      <div class="flex flex-col items-center gap-2 text-center pt-2">
        <div class="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
          <svg class="w-6 h-6 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7" />
          </svg>
        </div>
        <p class="text-sm font-semibold">Create your first job board</p>
        <p class="text-xs text-muted-foreground">Create your first board. You can edit the name on the dashboard later.</p>
      </div>
      <div class="flex flex-col gap-1.5">
        <Label for="board-name">Board name</Label>
        <Input
          id="board-name"
          v-model="newBoardName"
          type="text"
          placeholder="e.g. My Job Search"
          @keyup.enter="handleCreateBoard"
        />
      </div>
      <p v-if="createBoardError" class="text-xs text-destructive">{{ createBoardError }}</p>
      <Button @click="handleCreateBoard" :disabled="isCreatingBoard || !newBoardName.trim()" class="w-full">
        <svg v-if="isCreatingBoard" class="w-4 h-4 animate-spin mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
        </svg>
        {{ isCreatingBoard ? 'Creating...' : 'Create Board' }}
      </Button>
    </div>

    <!-- No job detected view -->
    <div v-else-if="view === 'no-job'" class="p-4 flex flex-col items-center gap-3 text-center">
      <div class="w-12 h-12 rounded-full bg-muted flex items-center justify-center">
        <svg class="w-6 h-6 text-muted-foreground/50" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
          <path stroke-linecap="round" stroke-linejoin="round"
            d="M20.25 14.15v4.073a2.25 2.25 0 01-2.25 2.25h-12a2.25 2.25 0 01-2.25-2.25v-4.073M15.75 9.75L12 6m0 0L8.25 9.75M12 6v12" />
        </svg>
      </div>
      <div>
        <p class="text-sm font-medium">Not a job listing</p>
        <p class="text-xs text-muted-foreground mt-1">Open a job posting on any job board and click the extension to import it.</p>
      </div>
    </div>

    <!-- Job capture view -->
    <div v-else-if="view === 'job'" class="p-4 flex flex-col gap-3">

      <!-- Already saved state -->
      <template v-if="existingJobId !== null">
        <div class="flex flex-col items-center gap-3 py-4 text-center">
          <div class="w-12 h-12 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
            <svg class="w-6 h-6 text-green-600 dark:text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <div>
            <p class="text-sm font-medium">Job saved already</p>
          </div>
          <a :href="`${config.appUrl}/boards/${selectedBoardId}?job=${existingJobId}`" target="_blank"
            class="text-xs text-primary hover:underline font-medium">
            View in Dashboard →
          </a>
        </div>
      </template>

      <!-- Skeleton loading state -->
      <template v-else-if="isFetchingData || isLoadingAts">
        <div class="flex flex-col gap-3">
          <!-- Board -->
          <div class="flex flex-col gap-1.5">
            <div class="h-3 w-10 rounded bg-muted animate-pulse"></div>
            <div class="h-9 rounded-md bg-muted animate-pulse"></div>
          </div>
          <!-- Title -->
          <div class="flex flex-col gap-1.5">
            <div class="h-3 w-14 rounded bg-muted animate-pulse"></div>
            <div class="h-9 rounded-md bg-muted animate-pulse"></div>
          </div>
          <!-- Company -->
          <div class="flex flex-col gap-1.5">
            <div class="h-3 w-16 rounded bg-muted animate-pulse"></div>
            <div class="h-9 rounded-md bg-muted animate-pulse"></div>
          </div>
          <!-- Location -->
          <div class="flex flex-col gap-1.5">
            <div class="h-3 w-14 rounded bg-muted animate-pulse"></div>
            <div class="h-9 rounded-md bg-muted animate-pulse"></div>
          </div>
          <!-- Status + Work model -->
          <div class="grid grid-cols-2 gap-2">
            <div class="flex flex-col gap-1.5">
              <div class="h-3 w-10 rounded bg-muted animate-pulse"></div>
              <div class="h-9 rounded-md bg-muted animate-pulse"></div>
            </div>
            <div class="flex flex-col gap-1.5">
              <div class="h-3 w-20 rounded bg-muted animate-pulse"></div>
              <div class="h-9 rounded-md bg-muted animate-pulse"></div>
            </div>
          </div>
          <!-- Notes -->
          <div class="flex flex-col gap-1.5">
            <div class="h-3 w-9 rounded bg-muted animate-pulse"></div>
            <div class="h-14 rounded-md bg-muted animate-pulse"></div>
          </div>
          <!-- Save button -->
          <div class="h-9 rounded-md bg-muted animate-pulse"></div>
          <p class="text-center text-xs text-muted-foreground">
            {{ isFetchingData ? 'Analysing page…' : 'Scoring your CV…' }}
          </p>
        </div>
      </template>

      <!-- Save form -->
      <template v-else>
        <p v-if="saveError" class="text-xs text-destructive text-center">{{ saveError }}</p>

        <!-- Board selector -->
        <div v-if="boards.length > 0" class="flex flex-col gap-1.5">
          <Label for="board-select">Board</Label>
          <NativeSelect
            id="board-select"
            :modelValue="selectedBoardId !== null ? String(selectedBoardId) : ''"
            @update:modelValue="selectedBoardId = Number($event)"
          >
            <option v-for="b in boards" :key="b.id" :value="String(b.id)">{{ b.name }}</option>
          </NativeSelect>
        </div>

        <!-- Job Title -->
        <div class="flex flex-col gap-1.5">
          <Label for="job-title">Job Title</Label>
          <Input id="job-title" v-model="jobTitle" type="text" placeholder="e.g. Software Engineer" />
        </div>

        <!-- Company -->
        <div class="flex flex-col gap-1.5">
          <Label for="company">Company</Label>
          <Image :src="company.logo_url" :alt="company.name" />
          <Input id="company" v-model="company.name" type="text" placeholder="e.g. Acme Corp" />
        </div>

        <!-- Location -->
        <div class="flex flex-col gap-1.5">
          <Label for="location">Location</Label>
          <Input id="location" v-model="jobLocation" type="text" placeholder="e.g. San Francisco, CA" />
        </div>

        <!-- Status + Work Model row -->
        <div class="grid grid-cols-2 gap-2">
          <div class="flex flex-col gap-1.5">
            <Label for="status">Status</Label>
            <NativeSelect id="status" v-model="jobStatus">
              <option v-for="s in statusOptions" :key="s" :value="s">{{ s }}</option>
            </NativeSelect>
          </div>
          <div class="flex flex-col gap-1.5">
            <Label for="work-model">Work Model</Label>
            <NativeSelect id="work-model" v-model="workModel">
              <option value="On-site">On-site</option>
              <option value="Remote">Remote</option>
              <option value="Hybrid">Hybrid</option>
            </NativeSelect>
          </div>
        </div>

        <!-- Notes -->
        <div class="flex flex-col gap-1.5">
          <Label for="notes">Notes</Label>
          <Textarea id="notes" v-model="notes" placeholder="Optional notes..." class="resize-none" rows="2" />
        </div>

        <!-- ATS Score card -->
        <div class="rounded-md border border-border bg-muted/30 p-3 flex items-center gap-3">
          <!-- Score gauge -->
          <template v-if="atsReport">
            <div class="relative w-14 h-14 flex-shrink-0">
              <svg class="w-14 h-14 -rotate-90" viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="42" fill="none" stroke="currentColor" stroke-width="10" class="text-muted/40" />
                <circle
                  cx="50" cy="50" r="42"
                  fill="none"
                  :stroke="atsGaugeStroke"
                  stroke-width="10"
                  stroke-linecap="round"
                  :stroke-dasharray="263.9"
                  :stroke-dashoffset="263.9 - (atsReport.score / 100) * 263.9"
                  style="transition: stroke-dashoffset 0.6s ease"
                />
              </svg>
              <div class="absolute inset-0 flex flex-col items-center justify-center">
                <span class="text-sm font-bold leading-none">{{ Math.round(atsReport.score) }}</span>
              </div>
            </div>
            <div class="flex flex-col">
              <span class="text-xs font-semibold">ATS Match</span>
              <span class="text-xs text-muted-foreground">Score on how your CV matches with this JD</span>
            </div>
          </template>
          <!-- No resume uploaded -->
          <template v-else-if="noResume">
            <div class="w-14 h-14 rounded-full bg-muted/40 flex items-center justify-center flex-shrink-0">
              <svg class="w-6 h-6 text-muted-foreground/50" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div class="flex flex-col gap-1">
              <span class="text-xs font-semibold">No CV uploaded</span>
              <a :href="`${config.appUrl}/settings?tab=resumes`" target="_blank"
                class="text-xs text-primary hover:underline">Upload your CV to link to this job and get a match score →</a>
            </div>
          </template>
          <!-- No description to score -->
          <template v-else>
            <div class="w-14 h-14 rounded-full bg-muted/40 flex-shrink-0"></div>
            <span class="text-xs text-muted-foreground">No job description to score.</span>
          </template>
        </div>

        <!-- Save + Re-fetch -->
        <div class="flex flex-col gap-2">
          <Button @click="saveJob" :disabled="isSaveBtnLoading || !jobTitle" class="w-full">
            <svg v-if="isSaveBtnLoading" class="w-4 h-4 animate-spin mr-2" xmlns="http://www.w3.org/2000/svg" fill="none"
              viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
            </svg>
            {{ isSaveBtnLoading ? 'Saving...' : 'Save Job' }}
          </Button>
          <button @click="retryFetch" class="text-xs text-muted-foreground hover:text-primary text-center transition">
            Re-analyse page
          </button>
        </div>
      </template>
    </div>

    <!-- Footer -->
    <div class="px-4 py-2 border-t border-border">
      <a :href="`${config.appUrl}/boards`" target="_blank"
        class="block text-center text-xs text-primary hover:underline">
        Open Dashboard →
      </a>
    </div>
  </div>
</template>

<style scoped>
.popup-container {
  min-width: 320px;
  max-width: 360px;
}
</style>
