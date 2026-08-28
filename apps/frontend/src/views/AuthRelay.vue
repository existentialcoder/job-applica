<script setup lang="ts">
import { onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

onMounted(async () => {
  const accessToken = route.query.access_token as string | undefined;
  const refreshToken = route.query.refresh_token as string | undefined;

  if (!accessToken) {
    router.replace('/login');
    return;
  }

  // setTokens fires ja:auth → webapp.ts content script → SYNC_AUTH → extension storage
  authStore.setTokens(accessToken, refreshToken);
  await authStore.fetchMe();

  if (authStore.isAuthenticated) {
    router.replace('/home');
  }
});
</script>

<template>
  <main class="h-screen w-screen flex items-center justify-center bg-background">
    <div class="flex flex-col items-center gap-3">
      <Icon name="LoaderCircle" :size="32" default-class="animate-spin text-primary" />
      <p class="text-sm text-muted-foreground">Completing sign-in from extension…</p>
    </div>
  </main>
</template>
