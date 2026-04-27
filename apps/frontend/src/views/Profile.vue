<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar';
import { useAuthStore } from '@/stores/auth';
import dataservice from '@/lib/dataservice';
import type { SkillData, ResumeData } from '@/lib/types';

const authStore = useAuthStore();
const route = useRoute();

const VALID_TABS = ['profile', 'skills', 'resumes', 'preferences', 'security'];
const activeTab = ref(VALID_TABS.includes(route.query.tab as string) ? (route.query.tab as string) : 'profile');

watch(() => route.query.tab, (tab) => {
  if (tab && VALID_TABS.includes(tab as string)) activeTab.value = tab as string;
});

watch(activeTab, (tab) => {
  if (tab === 'skills') loadSkills();
  if (tab === 'resumes') loadResumes();
});

// ── Profile tab ───────────────────────────────────────────────────────────────
const firstName      = ref(authStore.user?.first_name ?? '');
const lastName       = ref(authStore.user?.last_name ?? '');
const avatarUrl      = ref(authStore.user?.avatar_url ?? '');
const avatarUploading = ref(false);
const savingProfile  = ref(false);
const profileMsg     = ref('');

const initials = computed(() => {
  return `${firstName.value[0] ?? ''}${lastName.value[0] ?? ''}`.toUpperCase() || '?';
});

async function handleAvatarChange(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0];
  if (!file) return;
  avatarUploading.value = true;
  try {
    const { avatar_url } = await dataservice.uploadAvatar(file);
    avatarUrl.value = avatar_url;
    authStore.setUser({ ...authStore.user!, avatar_url });
  } catch {
    // ignore upload error silently — avatar stays as-is
  } finally {
    avatarUploading.value = false;
    (e.target as HTMLInputElement).value = '';
  }
}

async function saveProfile() {
  savingProfile.value = true;
  profileMsg.value = '';
  try {
    const updated = await dataservice.updateProfile({
      first_name: firstName.value,
      last_name: lastName.value,
    });
    authStore.setUser({ ...authStore.user!, ...updated });
    profileMsg.value = 'Saved';
  } catch {
    profileMsg.value = 'Failed to save';
  } finally {
    savingProfile.value = false;
  }
}

// ── Skills tab ────────────────────────────────────────────────────────────────
const userSkills    = ref<SkillData[]>([]);
const allSkills     = ref<SkillData[]>([]);
const skillSearch   = ref('');
const skillsLoaded  = ref(false);

const filteredSkills = computed(() => {
  const q = skillSearch.value.toLowerCase();
  return allSkills.value.filter(
    s => !userSkills.value.find(u => u.id === s.id) &&
         (s.label.toLowerCase().includes(q) || s.name.toLowerCase().includes(q))
  );
});

async function loadSkills() {
  if (skillsLoaded.value) return;
  [userSkills.value, allSkills.value] = await Promise.all([
    dataservice.getUserSkills(),
    dataservice.getSkills(),
  ]);
  skillsLoaded.value = true;
}

async function addSkill(skill: SkillData) {
  userSkills.value = await dataservice.addUserSkill(skill.id);
}

async function removeSkill(skillId: number) {
  userSkills.value = await dataservice.removeUserSkill(skillId);
}

// ── Resumes tab ───────────────────────────────────────────────────────────────
const resumes       = ref<ResumeData[]>([]);
const resumesLoaded = ref(false);
const uploading     = ref(false);
const uploadError   = ref('');

async function loadResumes() {
  if (resumesLoaded.value) return;
  resumes.value = await dataservice.getResumes();
  resumesLoaded.value = true;
}

async function handleFileChange(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0];
  if (!file) return;
  uploading.value = true;
  uploadError.value = '';
  try {
    const resume = await dataservice.uploadResume(file);
    resumes.value.unshift(resume);
  } catch (err: any) {
    uploadError.value = err.message ?? 'Upload failed';
  } finally {
    uploading.value = false;
    (e.target as HTMLInputElement).value = '';
  }
}

async function deleteResume(id: number) {
  await dataservice.deleteResume(id);
  resumes.value = resumes.value.filter(r => r.id !== id);
}

function formatSize(bytes: number | null) {
  if (!bytes) return '—';
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

// ── Preferences tab ───────────────────────────────────────────────────────────
const ghostedDays   = ref(14);
const stuckDays     = ref(7);
const savingPrefs   = ref(false);
const prefsMsg      = ref('');

async function loadPreferences() {
  const s = await dataservice.getSettings();
  ghostedDays.value = (s.ghosted_days as number) ?? 14;
  stuckDays.value   = (s.stuck_days as number) ?? 7;
}

async function savePreferences() {
  savingPrefs.value = true;
  prefsMsg.value = '';
  try {
    await dataservice.updateSettings({ ghosted_days: ghostedDays.value, stuck_days: stuckDays.value });
    prefsMsg.value = 'Saved';
  } catch {
    prefsMsg.value = 'Failed to save';
  } finally {
    savingPrefs.value = false;
  }
}

// ── Security tab ──────────────────────────────────────────────────────────────
const isOAuthUser   = computed(() => authStore.user?.signup_key === 'EMAIL' ? false : true);
const currentPw     = ref('');
const newPw         = ref('');
const confirmPw     = ref('');
const savingPw      = ref(false);
const pwMsg         = ref('');
const pwError       = ref('');

async function changePassword() {
  pwError.value = '';
  pwMsg.value = '';
  if (newPw.value !== confirmPw.value) {
    pwError.value = 'New passwords do not match';
    return;
  }
  if (newPw.value.length < 8) {
    pwError.value = 'Password must be at least 8 characters';
    return;
  }
  savingPw.value = true;
  try {
    await dataservice.changePassword({ current_password: currentPw.value, new_password: newPw.value });
    pwMsg.value = 'Password updated';
    currentPw.value = '';
    newPw.value = '';
    confirmPw.value = '';
  } catch (err: any) {
    pwError.value = err.message ?? 'Failed to change password';
  } finally {
    savingPw.value = false;
  }
}

// ── Init ──────────────────────────────────────────────────────────────────────
onMounted(() => {
  loadPreferences();
});

</script>

<template>
  <div class="p-6">
    <div class="mb-6">
      <h1 class="text-2xl font-bold tracking-tight">Settings</h1>
      <p class="text-sm text-muted-foreground mt-0.5">Manage your profile, skills, CVs and preferences</p>
    </div>

    <Tabs v-model="activeTab">
      <TabsList class="mb-6">
        <TabsTrigger value="profile">Profile</TabsTrigger>
        <TabsTrigger value="skills">Skills</TabsTrigger>
        <TabsTrigger value="resumes">Resumes</TabsTrigger>
        <TabsTrigger value="preferences">Preferences</TabsTrigger>
        <TabsTrigger value="security">Security</TabsTrigger>
      </TabsList>

      <!-- ── Profile ─────────────────────────────────────────────────────── -->
      <TabsContent value="profile">
        <div class="rounded-xl border bg-card p-6 space-y-6">
          <div class="flex items-center gap-5">
            <label class="relative cursor-pointer group">
              <Avatar class="h-16 w-16">
                <AvatarImage v-if="avatarUrl" :src="avatarUrl" alt="Avatar" />
                <AvatarFallback class="text-lg font-semibold">{{ initials }}</AvatarFallback>
              </Avatar>
              <div class="absolute inset-0 rounded-full bg-black/50 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                <svg v-if="!avatarUploading" class="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"/>
                  <path stroke-linecap="round" stroke-linejoin="round" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"/>
                </svg>
                <svg v-else class="w-4 h-4 text-white animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
                </svg>
              </div>
              <input type="file" class="sr-only" accept="image/*" :disabled="avatarUploading" @change="handleAvatarChange" />
            </label>
            <div>
              <p class="text-sm font-medium">Profile photo</p>
              <p class="text-xs text-muted-foreground mt-0.5">Click the avatar to upload a new photo (JPEG, PNG, WebP)</p>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div class="space-y-1.5">
              <label class="text-sm font-medium">First name</label>
              <Input v-model="firstName" />
            </div>
            <div class="space-y-1.5">
              <label class="text-sm font-medium">Last name</label>
              <Input v-model="lastName" />
            </div>
          </div>

          <div class="space-y-1.5">
            <label class="text-sm font-medium">Email</label>
            <Input :model-value="authStore.user?.email ?? authStore.user?.user_name ?? ''" disabled />
          </div>

          <div class="flex items-center gap-3">
            <Button @click="saveProfile" :disabled="savingProfile">
              {{ savingProfile ? 'Saving…' : 'Save changes' }}
            </Button>
            <span v-if="profileMsg" class="text-sm" :class="profileMsg === 'Saved' ? 'text-emerald-500' : 'text-destructive'">
              {{ profileMsg }}
            </span>
          </div>
        </div>
      </TabsContent>

      <!-- ── Skills ──────────────────────────────────────────────────────── -->
      <TabsContent value="skills">
        <div class="rounded-xl border bg-card p-6 space-y-5">
          <div>
            <p class="text-sm font-semibold">Your skills</p>
            <p class="text-xs text-muted-foreground mt-0.5">Used to match against job requirements</p>
          </div>

          <div v-if="userSkills.length" class="flex flex-wrap gap-2">
            <div
              v-for="skill in userSkills"
              :key="skill.id"
              class="flex items-center gap-1.5 bg-indigo-500/10 text-indigo-400 text-xs font-medium px-2.5 py-1 rounded-full"
            >
              <img v-if="skill.logo_url" :src="skill.logo_url" class="w-3.5 h-3.5 rounded-sm" />
              {{ skill.label }}
              <button @click="removeSkill(skill.id)" class="ml-0.5 opacity-60 hover:opacity-100">×</button>
            </div>
          </div>
          <p v-else class="text-sm text-muted-foreground">No skills added yet.</p>

          <div class="border-t pt-4 space-y-3">
            <p class="text-sm font-medium">Add skills</p>
            <Input v-model="skillSearch" placeholder="Search skills…" />
            <div class="flex flex-wrap gap-2 max-h-48 overflow-y-auto">
              <button
                v-for="skill in filteredSkills.slice(0, 40)"
                :key="skill.id"
                @click="addSkill(skill)"
                class="flex items-center gap-1.5 bg-muted hover:bg-muted/80 text-xs font-medium px-2.5 py-1 rounded-full transition-colors"
              >
                <img v-if="skill.logo_url" :src="skill.logo_url" class="w-3.5 h-3.5 rounded-sm" />
                {{ skill.label }}
              </button>
              <p v-if="!filteredSkills.length" class="text-xs text-muted-foreground">No matching skills</p>
            </div>
          </div>
        </div>
      </TabsContent>

      <!-- ── Resumes ─────────────────────────────────────────────────────── -->
      <TabsContent value="resumes">
        <div class="rounded-xl border bg-card p-6 space-y-5">
          <div>
            <p class="text-sm font-semibold">Uploaded CVs</p>
            <p class="text-xs text-muted-foreground mt-0.5">PDF or Word documents — max 10 MB each. Link any CV to a job from the job detail panel.</p>
          </div>

          <!-- Upload -->
          <label class="flex items-center gap-3 border-2 border-dashed border-border rounded-lg p-4 cursor-pointer hover:border-indigo-500/50 transition-colors">
            <input type="file" class="sr-only" accept=".pdf,.doc,.docx" @change="handleFileChange" :disabled="uploading" />
            <div class="w-9 h-9 rounded-lg bg-indigo-500/10 flex items-center justify-center flex-shrink-0">
              <svg class="w-4 h-4 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"/>
              </svg>
            </div>
            <div class="min-w-0">
              <p class="text-sm font-medium">{{ uploading ? 'Uploading…' : 'Click to upload a CV' }}</p>
              <p class="text-xs text-muted-foreground">PDF, DOC, DOCX</p>
            </div>
          </label>
          <p v-if="uploadError" class="text-sm text-destructive">{{ uploadError }}</p>

          <!-- List -->
          <div v-if="resumes.length" class="space-y-2">
            <div
              v-for="resume in resumes"
              :key="resume.id"
              class="flex items-center gap-3 rounded-lg border bg-muted/30 px-4 py-3"
            >
              <svg class="w-5 h-5 text-muted-foreground flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
              </svg>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium truncate">{{ resume.original_name }}</p>
                <p class="text-xs text-muted-foreground">{{ formatSize(resume.file_size) }}</p>
              </div>
              <a :href="resume.url" target="_blank" class="text-xs text-indigo-400 hover:underline flex-shrink-0">View</a>
              <button @click="deleteResume(resume.id)" class="text-xs text-muted-foreground hover:text-destructive transition-colors flex-shrink-0">Delete</button>
            </div>
          </div>
          <p v-else-if="resumesLoaded" class="text-sm text-muted-foreground">No CVs uploaded yet.</p>
        </div>
      </TabsContent>

      <!-- ── Preferences ─────────────────────────────────────────────────── -->
      <TabsContent value="preferences">
        <div class="rounded-xl border bg-card p-6 space-y-6">
          <div>
            <p class="text-sm font-semibold">Dashboard thresholds</p>
            <p class="text-xs text-muted-foreground mt-0.5">Control when applications are flagged in your analytics</p>
          </div>

          <div class="grid grid-cols-2 gap-6">
            <div class="space-y-1.5">
              <label class="text-sm font-medium">Ghosted after (days)</label>
              <Input v-model.number="ghostedDays" type="number" min="1" max="90" />
              <p class="text-xs text-muted-foreground">Applications in "Applied" with no update for this many days</p>
            </div>
            <div class="space-y-1.5">
              <label class="text-sm font-medium">Stuck after (days)</label>
              <Input v-model.number="stuckDays" type="number" min="1" max="90" />
              <p class="text-xs text-muted-foreground">Any active stage with no update for this many days</p>
            </div>
          </div>

          <div class="flex items-center gap-3">
            <Button @click="savePreferences" :disabled="savingPrefs">
              {{ savingPrefs ? 'Saving…' : 'Save preferences' }}
            </Button>
            <span v-if="prefsMsg" class="text-sm" :class="prefsMsg === 'Saved' ? 'text-emerald-500' : 'text-destructive'">
              {{ prefsMsg }}
            </span>
          </div>
        </div>
      </TabsContent>

      <!-- ── Security ────────────────────────────────────────────────────── -->
      <TabsContent value="security">
        <div class="rounded-xl border bg-card p-6 space-y-5">
          <div v-if="isOAuthUser" class="flex items-start gap-3 text-sm text-muted-foreground">
            <svg class="w-5 h-5 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            <p>Your account uses Google or LinkedIn sign-in. Password management is handled by your provider.</p>
          </div>

          <template v-else>
            <div>
              <p class="text-sm font-semibold">Change password</p>
              <p class="text-xs text-muted-foreground mt-0.5">Minimum 8 characters</p>
            </div>

            <div class="space-y-3 max-w-sm">
              <div class="space-y-1.5">
                <label class="text-sm font-medium">Current password</label>
                <Input v-model="currentPw" type="password" autocomplete="current-password" />
              </div>
              <div class="space-y-1.5">
                <label class="text-sm font-medium">New password</label>
                <Input v-model="newPw" type="password" autocomplete="new-password" />
              </div>
              <div class="space-y-1.5">
                <label class="text-sm font-medium">Confirm new password</label>
                <Input v-model="confirmPw" type="password" autocomplete="new-password" />
              </div>
            </div>

            <div class="flex items-center gap-3">
              <Button @click="changePassword" :disabled="savingPw">
                {{ savingPw ? 'Updating…' : 'Update password' }}
              </Button>
              <span v-if="pwMsg" class="text-sm text-emerald-500">{{ pwMsg }}</span>
              <span v-if="pwError" class="text-sm text-destructive">{{ pwError }}</span>
            </div>
          </template>
        </div>
      </TabsContent>

    </Tabs>
  </div>
</template>
