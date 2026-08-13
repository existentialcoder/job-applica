<script setup lang="ts">
import { computed, onMounted } from 'vue';
import { RouterView } from 'vue-router';
import { Toaster } from 'vue-sonner';
import { ScrollArea, ScrollBar } from '@/components/ui/scroll-area';
import { useAppStore } from '@/stores/app';
import { useAuthStore } from '@/stores/auth';
import { useFeatureStore } from '@/stores/features';

const appStore = useAppStore();
const toasterTheme = computed(() => (appStore.isDark ? 'dark' : 'light'));

async function handleTokenMessageFromExtension(e: Event) {
  const { access_token, refresh_token } = (
    e as CustomEvent<{ access_token: string | null; refresh_token: string | null }>
  ).detail;

  const authStore = useAuthStore();
  if (access_token) {
    authStore.setTokens(access_token, refresh_token ?? undefined);
    await authStore.fetchMe();
  } else {
    authStore.clearAuth();
  }
}

onMounted(async () => {
  await useFeatureStore().load();
  await useAppStore().initTheme();

  const authStore = useAuthStore();
  if (authStore.isAuthenticated) {
    await authStore.fetchMe();
  }

  window.addEventListener('ja:token-from-extension', handleTokenMessageFromExtension);
});
</script>

<template>
  <Toaster position="top-right" rich-colors :theme="toasterTheme" />
  <ScrollArea class="h-screen">
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" :key="$route.path" />
      </transition>
    </router-view>
    <ScrollBar class="z-50" />
  </ScrollArea>
</template>
