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

  authStore.setTokens(accessToken, refreshToken);
  await authStore.fetchMe();

  // Only navigate if fetchMe didn't already redirect to /login
  if (authStore.isAuthenticated) {
    router.replace('/home');
  }
});
</script>

<template>
  <main class="h-screen w-screen flex items-center justify-center bg-background">
    <div class="flex flex-col items-center gap-3">
      <Loader :size="32" variant="dew" />
      <p class="text-sm text-muted-foreground">Signing you in…</p>
    </div>
  </main>
</template>
