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

  if (accessToken) {
    authStore.setTokens(accessToken, refreshToken);
    await authStore.fetchMe();
    router.replace('/applications');
  } else {
    router.replace('/login');
  }
});
</script>

<template>
  <main class="h-screen w-screen flex items-center justify-center bg-background">
    <div class="flex flex-col items-center gap-3">
      <svg class="w-8 h-8 animate-spin text-primary" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
      </svg>
      <p class="text-sm text-muted-foreground">Completing sign-in from extension…</p>
    </div>
  </main>
</template>
