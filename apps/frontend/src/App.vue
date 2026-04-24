<script setup lang="ts">
import { RouterView } from 'vue-router'
import { onMounted } from 'vue';
import { useAppStore } from '@/stores/app';
import { useAuthStore } from '@/stores/auth';
import { ScrollArea, ScrollBar } from './components/ui/scroll-area';
import { Toaster } from 'vue-sonner';

onMounted(async () => {
  await useAppStore().initTheme();

  // Extension → Web app SSO: apply token received from extension login/logout.
  // content-webapp.js re-dispatches APPLY_TOKEN messages as this custom event.
  window.addEventListener('ja:token-from-extension', async (e: Event) => {
    const { access_token, refresh_token } = (e as CustomEvent<{ access_token: string | null; refresh_token: string | null }>).detail;
    const authStore = useAuthStore();
    if (access_token) {
      authStore.setTokens(access_token, refresh_token ?? undefined);
      await authStore.fetchMe();
    } else {
      authStore.clearAuth();
    }
  });
});
</script>

<template>
  <Toaster position="top-right" rich-colors />
  <ScrollArea class="h-screen">
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" :key="$route.path" />
      </transition>
    </router-view>
    <ScrollBar class="z-50" />
  </ScrollArea>
</template>
