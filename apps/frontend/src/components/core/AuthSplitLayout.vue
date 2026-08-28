<script setup lang="ts">
import { DewLogo } from '@job-applica/ui';
import AuthSidebarArt from './AuthSidebarArt.vue';

defineSlots<{ default: () => unknown }>();
</script>

<template>
  <div class="min-h-screen w-screen grid md:grid-cols-2 bg-background">
    <aside
      class="hidden md:block relative overflow-hidden bg-gradient-to-br from-[#312E81] via-[#4F46E5] to-[#7C3AED]"
      aria-hidden="true"
    >
      <div class="sticky top-0 h-screen flex flex-col">
        <div
          class="absolute -top-24 -left-24 w-96 h-96 rounded-full bg-white/10 blur-3xl pointer-events-none"
        ></div>
        <div
          class="absolute bottom-0 right-0 w-[28rem] h-[28rem] rounded-full bg-violet-300/20 blur-3xl pointer-events-none"
        ></div>
        <div class="relative pt-10 px-10">
          <DewLogo :size="36" show-wordmark wordmark-color="white" uid="authsplit-dew" />
        </div>
        <div class="relative flex-1 flex items-center justify-center px-4">
          <AuthSidebarArt class="w-full max-w-[400px]" />
        </div>
        <div class="relative px-10 pb-10">
          <p class="text-base text-indigo-200 font-medium tracking-wide">
            Your job search should not be a full-time job!
          </p>
        </div>
      </div>
    </aside>
    <main class="h-screen w-full flex items-center justify-center">
      <div class="w-full max-w-[400px] px-6"><slot /></div>
    </main>
  </div>
</template>

<style>
@keyframes briefcase-zoom {
  0%,
  100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.12);
  }
}
@keyframes spotlight-pulse {
  0%,
  100% {
    opacity: 0;
  }
  50% {
    opacity: 0.25;
  }
}
.spotlight-brief {
  transform-box: view-box;
  transform-origin: 215px 184px;
  animation: briefcase-zoom 4s ease-in-out infinite;
}
.spotlight-flash {
  animation: spotlight-pulse 2.5s ease-in-out infinite;
}
</style>
