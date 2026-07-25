<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { toast } from '@/lib/toast';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar';
import { useAuthStore } from '@/stores/auth';
import { useAppStore, BG_THEMES } from '@/stores/app';
import dataservice from '@/lib/dataservice';
import { cn } from '@/lib/utils';

const authStore = useAuthStore();
const appStore = useAppStore();
const route = useRoute();
const router = useRouter();

const VALID_TABS = ['profile', 'preferences'];
const activeTab = ref(VALID_TABS.includes(route.query.tab as string) ? (route.query.tab as string) : 'profile');

watch(() => route.query.tab, (tab) => {
  if (tab && VALID_TABS.includes(tab as string)) activeTab.value = tab as string;
});

watch(activeTab, (tab) => {
  router.replace({ query: { ...route.query, tab } });
});

// ── Profile ───────────────────────────────────────────────────────────────────
const firstName       = ref(authStore.user?.first_name ?? '');
const lastName        = ref(authStore.user?.last_name ?? '');
const avatarUrl       = ref(authStore.user?.avatar_url ?? '');
const avatarUploading = ref(false);
const savingProfile   = ref(false);

const initials = computed(() =>
  `${firstName.value[0] ?? ''}${lastName.value[0] ?? ''}`.toUpperCase() || '?'
);

async function handleAvatarChange(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0];
  if (!file) return;
  avatarUploading.value = true;
  try {
    const { avatar_url } = await dataservice.uploadAvatar(file);
    avatarUrl.value = avatar_url;
    authStore.setUser({ ...authStore.user!, avatar_url });
    toast.success('Avatar updated');
  } catch {
    toast.error('Failed to upload avatar');
  } finally {
    avatarUploading.value = false;
    (e.target as HTMLInputElement).value = '';
  }
}

async function saveProfile() {
  savingProfile.value = true;
  try {
    const updated = await dataservice.updateProfile({ first_name: firstName.value, last_name: lastName.value });
    authStore.setUser({ ...authStore.user!, ...updated });
    toast.success('Profile saved');
  } catch {
    toast.error('Failed to save profile');
  } finally {
    savingProfile.value = false;
  }
}


// ── Security ──────────────────────────────────────────────────────────────────
const passwordChangeEnabled   = computed(() => authStore.user?.has_password ?? false);
const currentPw     = ref('');
const newPw         = ref('');
const confirmPw     = ref('');
const savingPw      = ref(false);
const pwError       = ref('');

async function changePassword() {
  pwError.value = '';
  if (newPw.value !== confirmPw.value) { pwError.value = 'New passwords do not match'; return; }
  if (newPw.value.length < 8) { pwError.value = 'Password must be at least 8 characters'; return; }
  savingPw.value = true;
  try {
    await dataservice.changePassword({ current_password: currentPw.value, new_password: newPw.value });
    toast.success('Password updated');
    currentPw.value = ''; newPw.value = ''; confirmPw.value = '';
  } catch (err: any) {
    toast.error(err.message ?? 'Failed to change password');
  } finally {
    savingPw.value = false;
  }
}

onMounted(() => {
  appStore.setBreadcrumbs([{ label: 'Settings' }]);
});
</script>

<template>
  <div class="p-6">
    <div class="mb-6">
      <h1 class="text-2xl font-bold tracking-tight">Settings</h1>
      <p class="text-sm text-muted-foreground mt-0.5">Manage your profile and preferences</p>
    </div>

    <Tabs v-model="activeTab">
      <TabsList class="mb-6">
        <TabsTrigger value="profile">Profile</TabsTrigger>
        <TabsTrigger value="preferences">Appearance</TabsTrigger>
      </TabsList>

      <!-- ── Profile tab ──────────────────────────────────────────────────── -->
      <TabsContent value="profile" class="space-y-0">
        <div class="grid grid-cols-2 gap-6">

          <!-- Identity -->
          <div class="rounded-xl border bg-card p-6 space-y-5">
            <div>
              <p class="text-sm font-semibold">Identity</p>
              <p class="text-xs text-muted-foreground mt-0.5">Your name and profile photo</p>
            </div>

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
                <p class="text-xs text-muted-foreground mt-0.5">Click the avatar to upload (JPEG, PNG, WebP)</p>
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
              <label class="text-sm font-medium">{{authStore.user?.email ? 'Email' : 'Username'}}</label>
              <Input :model-value="authStore.user?.email ?? authStore.user?.user_name ?? ''" disabled />
            </div>

            <Button @click="saveProfile" :disabled="savingProfile">
              {{ savingProfile ? 'Saving…' : 'Save changes' }}
            </Button>
          </div>

          <!-- Security -->
          <div class="rounded-xl border bg-card p-6 space-y-5">
            <div>
              <p class="text-sm font-semibold">Security</p>
              <p class="text-xs text-muted-foreground mt-0.5">Manage your password</p>
            </div>
            <div v-if="!passwordChangeEnabled" class="flex items-start gap-2 text-sm text-muted-foreground">
              <svg class="w-5 h-5 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
              <p>Your account uses Google or LinkedIn sign-in. Password management is handled by your provider.</p>
            </div>

            <template v-else>
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
                  {{ savingPw ? 'Updating…' : 'Update' }}
                </Button>
                <span v-if="pwError" class="text-sm text-destructive">{{ pwError }}</span>
              </div>
            </template>
          </div>

        </div>
      </TabsContent>

      <!-- ── Preferences tab ──────────────────────────────────────────────── -->
      <TabsContent value="preferences" class="space-y-0">
        <div class="rounded-xl border bg-card divide-y divide-border">

          <!-- Mode -->
          <div class="p-6 space-y-5">
            <div>
              <p class="text-sm font-semibold">Mode</p>
              <p class="text-xs text-muted-foreground mt-0.5">Choose your preferred color scheme</p>
            </div>

            <div class="flex gap-2">
              <button
                v-for="mode in (['light', 'dark', 'system'] as const)"
                :key="mode"
                :class="cn(
                  'flex-1 flex flex-col items-center gap-2 rounded-lg border-2 p-3 text-xs font-medium transition-colors capitalize',
                  appStore.themeMode === mode
                    ? 'border-primary text-primary'
                    : 'border-border text-muted-foreground hover:border-primary/40 hover:text-foreground'
                )"
                @click="appStore.setThemeMode(mode)"
              >
                <!-- Light icon -->
                <svg v-if="mode === 'light'" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M12 3v2.25m6.364.386l-1.591 1.591M21 12h-2.25m-.386 6.364l-1.591-1.591M12 18.75V21m-4.773-4.227l-1.591 1.591M5.25 12H3m4.227-4.773L5.636 5.636M15.75 12a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0z" />
                </svg>
                <!-- Dark icon -->
                <svg v-else-if="mode === 'dark'" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M21.752 15.002A9.718 9.718 0 0118 15.75c-5.385 0-9.75-4.365-9.75-9.75 0-1.33.266-2.597.748-3.752A9.753 9.753 0 003 11.25C3 16.635 7.365 21 12.75 21a9.753 9.753 0 009.002-5.998z" />
                </svg>
                <!-- System icon -->
                <svg v-else class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M9 17.25v1.007a3 3 0 01-.879 2.122L7.5 21h9l-.621-.621A3 3 0 0115 18.257V17.25m6-12V15a2.25 2.25 0 01-2.25 2.25H5.25A2.25 2.25 0 013 15V5.25m18 0A2.25 2.25 0 0018.75 3H5.25A2.25 2.25 0 003 5.25m18 0H3" />
                </svg>
                {{ mode }}
              </button>
            </div>
          </div>

          <!-- Themes -->
          <div class="p-6 space-y-5">
            <div>
              <p class="text-sm font-semibold">Themes</p>
              <p class="text-xs text-muted-foreground mt-0.5">
                Choose a theme for {{ appStore.isDark ? 'dark' : 'light' }} mode
              </p>
            </div>

            <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <button
                v-for="(theme, key) in (appStore.isDark ? BG_THEMES.dark : BG_THEMES.light)"
                :key="key"
                :class="cn(
                  'relative rounded-xl overflow-hidden border-2 transition-all text-left',
                  (appStore.isDark ? appStore.darkBgTheme : appStore.lightBgTheme) === key
                    ? 'border-primary shadow-sm'
                    : 'border-transparent hover:border-muted-foreground/20'
                )"
                @click="appStore.isDark ? appStore.setDarkBgTheme(key) : appStore.setLightBgTheme(key)"
              >
                <!-- Mini app mockup -->
                <div class="h-24 flex" :style="{ background: theme.body }">
                  <!-- Sidebar strip -->
                  <div
                    class="w-9 flex-shrink-0 flex flex-col gap-1 p-1.5 border-r"
                    :style="{ background: theme.preview.sidebar, borderColor: theme.preview.border }"
                  >
                    <div class="h-1.5 w-full rounded-sm" style="background: hsl(var(--primary) / 0.35)"/>
                    <div class="h-1.5 w-full rounded-sm" :style="{ background: theme.preview.skeleton }"/>
                    <div class="h-1.5 w-3/4 rounded-sm" :style="{ background: theme.preview.skeletonAlt }"/>
                    <div class="h-1.5 w-full rounded-sm" :style="{ background: theme.preview.skeletonAlt }"/>
                    <div class="h-1.5 w-2/3 rounded-sm" :style="{ background: theme.preview.skeletonAlt }"/>
                  </div>
                  <!-- Content -->
                  <div class="flex-1 p-1.5 flex flex-col gap-1.5">
                    <div class="flex items-center gap-1">
                      <div class="w-2 h-2 rounded-full border flex-shrink-0" :style="{ borderColor: theme.preview.skeleton }"/>
                      <div class="h-1.5 rounded-full flex-1" :style="{ background: theme.preview.skeleton }"/>
                    </div>
                    <div class="flex items-center gap-1">
                      <div class="w-2 h-2 rounded-full border flex-shrink-0" :style="{ borderColor: theme.preview.skeletonAlt }"/>
                      <div class="h-1.5 rounded-full w-3/4" :style="{ background: theme.preview.skeletonAlt }"/>
                    </div>
                    <div class="flex items-center gap-1">
                      <div class="w-2 h-2 rounded-full border flex-shrink-0" :style="{ borderColor: theme.preview.skeletonAlt }"/>
                      <div class="h-1.5 rounded-full w-1/2" :style="{ background: theme.preview.skeletonAlt }"/>
                    </div>
                  </div>
                </div>
                <!-- Footer: name + checkmark -->
                <div
                  class="flex items-center justify-between px-2.5 py-1.5 border-t"
                  :style="{ background: theme.preview.sidebar, borderColor: theme.preview.border }"
                >
                  <span
                    class="text-[11px] font-semibold leading-none"
                    :style="{ color: (appStore.isDark ? appStore.darkBgTheme : appStore.lightBgTheme) === key ? 'hsl(var(--primary))' : theme.preview.text }"
                  >{{ theme.label }}</span>
                  <svg
                    v-if="(appStore.isDark ? appStore.darkBgTheme : appStore.lightBgTheme) === key"
                    class="w-3 h-3 text-primary flex-shrink-0"
                    fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3"
                  >
                    <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5"/>
                  </svg>
                </div>
              </button>
            </div>
          </div>

        </div>
      </TabsContent>
    </Tabs>
  </div>
</template>
