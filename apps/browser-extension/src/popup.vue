<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue';
import dataservice, { type BoardData, type JobExtractResult, type CompanyResult, type ATSReport, type ExtractedLocation } from './lib/dataservice';
import ext from './lib/ext';
import { config, loadConfig, saveConfig, resetConfig } from './lib/config';
import { DEFAULT_COMPANY_LOGO_URL } from '@job-applica/ui/lib/constants';
import { DewLogo, GoogleLogo, LinkedInLogo, AtsGauge, Icon, Loader, Skeleton } from '@job-applica/ui';
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
      <DewLogo :size="22" show-wordmark uid="popup-dew" />
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
          <Icon name="Settings" :size="16" />
        </button>
        <!-- Dark mode toggle -->
        <button @click="toggleDark"
          class="p-1 rounded text-muted-foreground hover:text-foreground hover:bg-muted transition"
          :title="isDark ? 'Switch to light mode' : 'Switch to dark mode'">
          <Icon v-if="isDark" name="Sun" :size="16" />
          <Icon v-else name="Moon" :size="16" />
        </button>
      </div>
    </div>

    <!-- Settings view -->
    <div v-if="view === 'settings'" class="p-4 flex flex-col gap-4">
      <div class="flex items-center gap-2">
        <button @click="closeSettings" class="p-1 rounded text-muted-foreground hover:text-foreground hover:bg-muted transition" title="Back">
          <Icon name="ChevronLeft" :size="16" />
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
          <Skeleton class="h-3 w-10" />
          <Skeleton class="h-9 rounded-md" />
        </div>
        <div class="flex flex-col gap-1.5">
          <Skeleton class="h-3 w-14" />
          <Skeleton class="h-9 rounded-md" />
        </div>
        <div class="flex flex-col gap-1.5">
          <Skeleton class="h-3 w-16" />
          <Skeleton class="h-9 rounded-md" />
        </div>
        <div class="flex flex-col gap-1.5">
          <Skeleton class="h-3 w-14" />
          <Skeleton class="h-9 rounded-md" />
        </div>
        <div class="grid grid-cols-2 gap-2">
          <div class="flex flex-col gap-1.5">
            <Skeleton class="h-3 w-10" />
            <Skeleton class="h-9 rounded-md" />
          </div>
          <div class="flex flex-col gap-1.5">
            <Skeleton class="h-3 w-20" />
            <Skeleton class="h-9 rounded-md" />
          </div>
        </div>
        <div class="flex flex-col gap-1.5">
          <Skeleton class="h-3 w-9" />
          <Skeleton class="h-14 rounded-md" />
        </div>
        <Skeleton class="h-9 rounded-md" />
      </div>
    </div>

    <!-- Login view -->
    <div v-else-if="view === 'login'" class="p-4 flex flex-col gap-3">
      <p class="text-sm text-muted-foreground text-center">Sign in to stand out in your job search</p>

      <!-- OAuth buttons -->
      <Button variant="outline" class="w-full gap-2 justify-center" type="button"
        :disabled="isOAuthLoading !== null" @click="openOAuth('google')">
        <Loader v-if="isOAuthLoading === 'google'" :size="16" />
        <GoogleLogo v-else :size="16" />
        {{ isOAuthLoading === 'google' ? 'Opening…' : 'Continue with Google' }}
      </Button>

      <Button variant="outline" class="w-full gap-2 justify-center" type="button"
        :disabled="isOAuthLoading !== null" @click="openOAuth('linkedin')">
        <Loader v-if="isOAuthLoading === 'linkedin'" :size="16" />
        <LinkedInLogo v-else :size="16" />
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
        <Loader v-if="isLoginLoading" :size="16" class="mr-2" />
        {{ isLoginLoading ? 'Signing in...' : 'Sign In' }}
      </Button>
    </div>

    <!-- First-run setup view -->
    <div v-else-if="view === 'setup'" class="p-4 flex flex-col gap-4">
      <div class="flex flex-col items-center gap-2 text-center pt-2">
        <div class="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
          <Icon name="Kanban" :size="24" default-class="text-primary" />
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
        <Loader v-if="isCreatingBoard" :size="16" class="mr-2" />
        {{ isCreatingBoard ? 'Creating...' : 'Create Board' }}
      </Button>
    </div>

    <!-- No job detected view -->
    <div v-else-if="view === 'no-job'" class="p-4 flex flex-col items-center gap-3 text-center">
      <div class="w-12 h-12 rounded-full bg-muted flex items-center justify-center">
        <Icon name="Inbox" :size="24" default-class="text-muted-foreground/50" />
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
            <Icon name="Check" :size="24" default-class="text-green-600 dark:text-green-400" />
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
            <Skeleton class="h-3 w-10" />
            <Skeleton class="h-9 rounded-md" />
          </div>
          <!-- Title -->
          <div class="flex flex-col gap-1.5">
            <Skeleton class="h-3 w-14" />
            <Skeleton class="h-9 rounded-md" />
          </div>
          <!-- Company -->
          <div class="flex flex-col gap-1.5">
            <Skeleton class="h-3 w-16" />
            <Skeleton class="h-9 rounded-md" />
          </div>
          <!-- Location -->
          <div class="flex flex-col gap-1.5">
            <Skeleton class="h-3 w-14" />
            <Skeleton class="h-9 rounded-md" />
          </div>
          <!-- Status + Work model -->
          <div class="grid grid-cols-2 gap-2">
            <div class="flex flex-col gap-1.5">
              <Skeleton class="h-3 w-10" />
              <Skeleton class="h-9 rounded-md" />
            </div>
            <div class="flex flex-col gap-1.5">
              <Skeleton class="h-3 w-20" />
              <Skeleton class="h-9 rounded-md" />
            </div>
          </div>
          <!-- Notes -->
          <div class="flex flex-col gap-1.5">
            <Skeleton class="h-3 w-9" />
            <Skeleton class="h-14 rounded-md" />
          </div>
          <!-- Save button -->
          <Skeleton class="h-9 rounded-md" />
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
          <img
            :src="company.logo_url || DEFAULT_COMPANY_LOGO_URL"
            :alt="company.name"
            class="w-6 h-6 rounded-full object-contain bg-muted"
            @error="($event.target as HTMLImageElement).src = DEFAULT_COMPANY_LOGO_URL"
          />
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

        <!-- Match Score card -->
        <div class="rounded-md border border-border bg-muted/30 p-3 flex items-center gap-3">
          <!-- Score gauge -->
          <template v-if="atsReport">
            <AtsGauge :percentage="atsReport.score" :size="56" :stroke-width="10" :color="atsGaugeStroke">
              <span class="text-sm font-bold leading-none">{{ Math.round(atsReport.score) }}</span>
            </AtsGauge>
            <div class="flex flex-col">
              <span class="text-xs font-semibold">Match Score</span>
              <span class="text-xs text-muted-foreground">Score on how your CV matches with this JD</span>
            </div>
          </template>
          <!-- No resume uploaded -->
          <template v-else-if="noResume">
            <div class="w-14 h-14 rounded-full bg-muted/40 flex items-center justify-center flex-shrink-0">
              <Icon name="FileText" :size="24" default-class="text-muted-foreground/50" />
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
            <Loader v-if="isSaveBtnLoading" :size="16" class="mr-2" />
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
