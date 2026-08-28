<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import dataservice from '@/lib/dataservice';
import { toast } from '@/lib/toast';
import { cn } from '@/lib/utils';
import { useAppStore } from '@/stores/app';
import { useAuthStore } from '@/stores/auth';
import { useSettingsStore, BG_THEMES } from '@/stores/settings';

const authStore = useAuthStore();
const appStore = useAppStore();
const settingsStore = useSettingsStore();
const route = useRoute();
const router = useRouter();

const VALID_TABS = ['profile', 'preferences'];
const activeTab = ref(
  VALID_TABS.includes(route.query.tab as string) ? (route.query.tab as string) : 'profile'
);

watch(
  () => route.query.tab,
  (tab) => {
    if (tab && VALID_TABS.includes(tab as string)) activeTab.value = tab as string;
  }
);

watch(activeTab, (tab) => {
  router.replace({ query: { ...route.query, tab } });
});

// ── Profile ───────────────────────────────────────────────────────────────────
const firstName = ref(authStore.user?.first_name ?? '');
const lastName = ref(authStore.user?.last_name ?? '');
const avatarUrl = ref(authStore.user?.avatar_url ?? '');
const avatarUploading = ref(false);
const savingProfile = ref(false);

const initials = computed(
  () => `${firstName.value[0] ?? ''}${lastName.value[0] ?? ''}`.toUpperCase() || '?'
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
    avatarUploading.value = false
    ;(e.target as HTMLInputElement).value = '';
  }
}

async function saveProfile() {
  savingProfile.value = true;
  try {
    const updated = await dataservice.updateProfile({
      first_name: firstName.value,
      last_name: lastName.value
    });
    authStore.setUser({ ...authStore.user!, ...updated });
    toast.success('Profile saved');
  } catch {
    toast.error('Failed to save profile');
  } finally {
    savingProfile.value = false;
  }
}

// ── Security ──────────────────────────────────────────────────────────────────
const passwordChangeEnabled = computed(() => authStore.user?.has_password ?? false);
const currentPw = ref('');
const newPw = ref('');
const confirmPw = ref('');
const savingPw = ref(false);
const pwError = ref('');

async function changePassword() {
  pwError.value = '';
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
    await dataservice.changePassword({
      current_password: currentPw.value,
      new_password: newPw.value
    });
    toast.success('Password updated');
    currentPw.value = '';
    newPw.value = '';
    confirmPw.value = '';
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
                <div
                  class="absolute inset-0 rounded-full bg-black/50 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <Icon
                    v-if="!avatarUploading"
                    name="Camera"
                    :size="20"
                    :stroke-width="2"
                    default-class="text-white"
                  />
                  <Icon
                    v-else
                    name="LoaderCircle"
                    :size="16"
                    default-class="text-white animate-spin"
                  />
                </div>
                <input
                  type="file"
                  class="sr-only"
                  accept="image/*"
                  :disabled="avatarUploading"
                  @change="handleAvatarChange"
                />
              </label>
              <div>
                <p class="text-sm font-medium">Profile photo</p>
                <p class="text-xs text-muted-foreground mt-0.5">
                  Click the avatar to upload (JPEG, PNG, WebP)
                </p>
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
              <label class="text-sm font-medium">{{
                authStore.user?.email ? 'Email' : 'Username'
              }}</label>
              <Input
                :model-value="authStore.user?.email ?? authStore.user?.user_name ?? ''"
                disabled
              />
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
            <div
              v-if="!passwordChangeEnabled"
              class="flex items-start gap-2 text-sm text-muted-foreground"
            >
              <Icon name="Info" :size="20" default-class="flex-shrink-0 mt-0.5" />
              <p>
                Your account uses Google or LinkedIn sign-in. Password management is handled by your
                provider.
              </p>
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
                v-for="mode in ['light', 'dark', 'system'] as const"
                :key="mode"
                :class="
                  cn(
                    'flex-1 flex flex-col items-center gap-2 rounded-lg border-2 p-3 text-xs font-medium transition-colors capitalize',
                    settingsStore.settings.themeMode === mode
                      ? 'border-primary text-primary'
                      : 'border-border text-muted-foreground hover:border-primary/40 hover:text-foreground'
                  )
                "
                @click="settingsStore.setThemeMode(mode)"
              >
                <!-- Light icon -->
                <Icon v-if="mode === 'light'" name="Sun" :size="20" />
                <!-- Dark icon -->
                <Icon v-else-if="mode === 'dark'" name="Moon" :size="20" />
                <!-- System icon -->
                <Icon v-else name="Monitor" :size="20" />
                {{ mode }}
              </button>
            </div>
          </div>

          <!-- Themes -->
          <div class="p-6 space-y-5">
            <div>
              <p class="text-sm font-semibold">Themes</p>
              <p class="text-xs text-muted-foreground mt-0.5">
                Choose a theme for {{ settingsStore.isDark ? 'dark' : 'light' }} mode
              </p>
            </div>

            <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <button
                v-for="(theme, key) in settingsStore.isDark ? BG_THEMES.dark : BG_THEMES.light"
                :key="key"
                :class="
                  cn(
                    'relative rounded-xl overflow-hidden border-2 transition-all text-left',
                    (settingsStore.isDark ? settingsStore.settings.darkBgTheme : settingsStore.settings.lightBgTheme) === key
                      ? 'border-primary shadow-sm'
                      : 'border-transparent hover:border-muted-foreground/20'
                  )
                "
                @click="
                  settingsStore.isDark ? settingsStore.setDarkBgTheme(key) : settingsStore.setLightBgTheme(key)
                "
              >
                <!-- Mini app mockup -->
                <div class="h-24 flex" :style="{ background: theme.body }">
                  <!-- Sidebar strip -->
                  <div
                    class="w-9 flex-shrink-0 flex flex-col gap-1 p-1.5 border-r"
                    :style="{
                      background: theme.preview.sidebar,
                      borderColor: theme.preview.border
                    }"
                  >
                    <div
                      class="h-1.5 w-full rounded-sm"
                      style="background: hsl(var(--primary) / 0.35)"
                    />
                    <div
                      class="h-1.5 w-full rounded-sm"
                      :style="{ background: theme.preview.skeleton }"
                    />
                    <div
                      class="h-1.5 w-3/4 rounded-sm"
                      :style="{ background: theme.preview.skeletonAlt }"
                    />
                    <div
                      class="h-1.5 w-full rounded-sm"
                      :style="{ background: theme.preview.skeletonAlt }"
                    />
                    <div
                      class="h-1.5 w-2/3 rounded-sm"
                      :style="{ background: theme.preview.skeletonAlt }"
                    />
                  </div>
                  <!-- Content -->
                  <div class="flex-1 p-1.5 flex flex-col gap-1.5">
                    <div class="flex items-center gap-1">
                      <div
                        class="w-2 h-2 rounded-full border flex-shrink-0"
                        :style="{ borderColor: theme.preview.skeleton }"
                      />
                      <div
                        class="h-1.5 rounded-full flex-1"
                        :style="{ background: theme.preview.skeleton }"
                      />
                    </div>
                    <div class="flex items-center gap-1">
                      <div
                        class="w-2 h-2 rounded-full border flex-shrink-0"
                        :style="{ borderColor: theme.preview.skeletonAlt }"
                      />
                      <div
                        class="h-1.5 rounded-full w-3/4"
                        :style="{ background: theme.preview.skeletonAlt }"
                      />
                    </div>
                    <div class="flex items-center gap-1">
                      <div
                        class="w-2 h-2 rounded-full border flex-shrink-0"
                        :style="{ borderColor: theme.preview.skeletonAlt }"
                      />
                      <div
                        class="h-1.5 rounded-full w-1/2"
                        :style="{ background: theme.preview.skeletonAlt }"
                      />
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
                    :style="{
                      color:
                        (settingsStore.isDark ? settingsStore.settings.darkBgTheme : settingsStore.settings.lightBgTheme) === key
                          ? 'hsl(var(--primary))'
                          : theme.preview.text
                    }"
                    >{{ theme.label }}</span
                  >
                  <Icon
                    v-if="(settingsStore.isDark ? settingsStore.settings.darkBgTheme : settingsStore.settings.lightBgTheme) === key"
                    name="Check"
                    :size="12"
                    :stroke-width="3"
                    default-class="text-primary flex-shrink-0"
                  />
                </div>
              </button>
            </div>
          </div>
        </div>
      </TabsContent>
    </Tabs>
  </div>
</template>
