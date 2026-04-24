<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import dataservice from './lib/dataservice';
import ext from './lib/ext';
import { Button } from '@job-applica/ui/components/ui/button';
import { Input } from '@job-applica/ui/components/ui/input';
import { Label } from '@job-applica/ui/components/ui/label';
import { Badge } from '@job-applica/ui/components/ui/badge';
import { NativeSelect } from '@job-applica/ui/components/ui/select';
import { Textarea } from '@job-applica/ui/components/ui/textarea';

const API_BASE = 'http://localhost:8000/api/v1';

// ── Dark mode ────────────────────────────────────────────────────────────────
const isDark = ref(false);

function applyDark(dark: boolean) {
  isDark.value = dark;
  document.documentElement.classList.toggle('dark', dark);
}

async function initDarkMode() {
  // Prefer cached value for instant render, then sync from API
  const cached = await ext.storage.local.get(['dark_mode']);
  if (typeof cached.dark_mode === 'boolean') applyDark(cached.dark_mode);

  // Fetch authoritative value from API (may differ if user changed from web app)
  try {
    const settings = await dataservice.getSettings();
    const dark = settings.theme === 'dark';
    applyDark(dark);
    ext.storage.local.set({ dark_mode: dark });
  } catch { /* offline — keep cached value */ }
}

async function toggleDark() {
  const next = !isDark.value;
  applyDark(next);
  ext.storage.local.set({ dark_mode: next });
  // Persist to API so web app picks it up on next load
  await dataservice.updateSettings({ theme: next ? 'dark' : 'light' });
}

// ── View state ──────────────────────────────────────────────────────────────
const view = ref<'login' | 'job' | 'no-job'>('no-job');

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
  ext.tabs.create({ url: `${API_BASE}/auth/${provider}?origin=extension` });
}

async function handleLogout() {
  await dataservice.logout();
  view.value = 'login';
}

// ── Job data ──────────────────────────────────────────────────────────────────
const platform = ref<string | null>(null);
const currentUrl = ref<string | null>(null);
const jobTitle = ref('');
const company = ref('');
const jobLocation = ref('');
const jobDescription = ref<string | null>(null);
const salaryRange = ref<string | null>(null);
const workModel = ref('On-site');
const jobStatus = ref('Saved');
const notes = ref('');
const existingJobId = ref<number | null>(null);
const isSaveBtnLoading = ref(false);
const saveError = ref('');
const isFetchingData = ref(false);

const STATUS_OPTIONS = ['Saved', 'Applied', 'Phone Screen', 'Interview', 'Technical', 'Offer', 'Rejected', 'Withdrawn'];

const addMessageListener = (callback: (msg: any) => void) => {
  ext.runtime.onMessage.addListener(callback);
};

async function setupData() {
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

  if (!url || !dataservice.isJobPage(url)) {
    view.value = 'no-job';
    return;
  }

  platform.value = dataservice.detectPlatform(url);
  view.value = 'job';

  addMessageListener(async (msg: any) => {
    if (msg.jobTitle) jobTitle.value = msg.jobTitle;
    if (msg.company) company.value = msg.company;
    if (msg.location) jobLocation.value = msg.location;
    if (msg.jobDescription) jobDescription.value = msg.jobDescription;
    if (msg.salaryRange) salaryRange.value = msg.salaryRange;
    if (msg.workModel) workModel.value = msg.workModel;
    isFetchingData.value = false;

    // Check by title + company once we have the data from the page
    if (msg.jobTitle) {
      existingJobId.value = await dataservice.checkJobExists(msg.jobTitle, msg.company || undefined);
    }
  });

  isFetchingData.value = true;
  try {
    await dataservice.fetchJobDataFromContentScript();
  } catch {
    isFetchingData.value = false;
  }
  // Stop spinner after 4s even if message never arrives (e.g. CSP block)
  setTimeout(() => { isFetchingData.value = false; }, 4000);
}

// Listen for storage changes written by background.js (OAuth + theme sync)
function onStorageChange(changes: Record<string, { newValue?: any; oldValue?: any }>) {
  if (changes.access_token?.newValue) {
    isOAuthLoading.value = null;
    setupData();
  }
  if ('dark_mode' in changes) {
    applyDark(changes.dark_mode.newValue === true);
  }
}

onMounted(async () => {
  await initDarkMode();
  ext.storage.onChanged.addListener(onStorageChange);
  await setupData();
});

onUnmounted(() => {
  ext.storage.onChanged.removeListener(onStorageChange);
});

async function retryFetch() {
  jobTitle.value = '';
  company.value = '';
  jobLocation.value = '';
  jobDescription.value = null;
  salaryRange.value = null;
  isFetchingData.value = true;
  try {
    await dataservice.fetchJobDataFromContentScript();
  } catch {
    isFetchingData.value = false;
  }
  setTimeout(() => { isFetchingData.value = false; }, 4000);
}

async function saveJob() {
  isSaveBtnLoading.value = true;
  saveError.value = '';

  try {
    const jobId = await dataservice.createJob({
      title: jobTitle.value,
      company_name: company.value || undefined,
      location: jobLocation.value || undefined,
      status: jobStatus.value,
      salary_range: salaryRange.value || undefined,
      description: jobDescription.value?.trim() || undefined,
      work_model: workModel.value,
      source_url: currentUrl.value || undefined,
      source_platform: platform.value || undefined,
      notes: notes.value || undefined,
    });

    if (jobId !== null) {
      existingJobId.value = jobId;
    } else {
      saveError.value = 'Failed to save. Please try again.';
    }
  } finally {
    isSaveBtnLoading.value = false;
  }
}

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
      <span class="text-sm font-bold">Job Applica</span>
      <div class="flex items-center gap-2">
        <Badge v-if="platform" :variant="platformBadgeVariant[platform] || 'secondary'" class="text-xs">
          {{ platform }}
        </Badge>
        <button v-if="view !== 'login'" @click="handleLogout"
          class="text-xs text-muted-foreground hover:text-destructive transition">
          Sign out
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

    <!-- Login view -->
    <div v-if="view === 'login'" class="p-4 flex flex-col gap-3">
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

    <!-- No job detected view -->
    <div v-else-if="view === 'no-job'" class="p-4 flex flex-col items-center gap-3 text-center">
      <svg class="w-10 h-10 text-muted-foreground/40" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
          d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
      </svg>
      <p class="text-sm text-muted-foreground">
        Navigate to a job listing on LinkedIn, Indeed, Glassdoor, Monster, ZipRecruiter, or Jobscan.
      </p>
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
            <p class="text-sm font-medium">Already in your tracker</p>
            <p class="text-xs text-muted-foreground mt-0.5">This job was saved previously.</p>
          </div>
          <a :href="`http://localhost:5173/applications?job=${existingJobId}`" target="_blank"
            class="text-xs text-primary hover:underline font-medium">
            View in Dashboard →
          </a>
        </div>
      </template>

      <!-- Save form (only when not already saved) -->
      <template v-else>
        <p v-if="saveError" class="text-xs text-destructive text-center">{{ saveError }}</p>

        <!-- Fetching indicator -->
        <div v-if="isFetchingData" class="flex items-center gap-2 text-xs text-muted-foreground">
          <svg class="w-3 h-3 animate-spin flex-shrink-0" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
          </svg>
          Auto-filling from page...
        </div>

        <!-- Job Title -->
        <div class="flex flex-col gap-1.5">
          <Label for="job-title">Job Title</Label>
          <Input id="job-title" v-model="jobTitle" type="text" placeholder="e.g. Software Engineer" />
        </div>

        <!-- Company -->
        <div class="flex flex-col gap-1.5">
          <Label for="company">Company</Label>
          <Input id="company" v-model="company" type="text" placeholder="e.g. Acme Corp" />
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
              <option v-for="s in STATUS_OPTIONS" :key="s" :value="s">{{ s }}</option>
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

        <!-- Description & retry row -->
        <div class="flex items-center justify-between">
          <span class="flex items-center gap-1 text-xs"
            :class="jobDescription ? 'text-green-600 dark:text-green-400' : 'text-muted-foreground'">
            <svg v-if="jobDescription" class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
            </svg>
            <svg v-else class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-3-3v6" />
            </svg>
            {{ jobDescription ? 'Description captured' : 'No description' }}
          </span>
          <button v-if="!isFetchingData" @click="retryFetch"
            class="text-xs text-primary hover:underline">
            Re-fetch
          </button>
        </div>

        <!-- Save button -->
        <Button @click="saveJob" :disabled="isSaveBtnLoading || !jobTitle" class="w-full">
          <svg v-if="isSaveBtnLoading" class="w-4 h-4 animate-spin mr-2" xmlns="http://www.w3.org/2000/svg" fill="none"
            viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
          </svg>
          {{ isSaveBtnLoading ? 'Saving...' : 'Save Job' }}
        </Button>
      </template>
    </div>

    <!-- Footer -->
    <div class="px-4 py-2 border-t border-border">
      <a href="http://localhost:5173/applications" target="_blank"
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
