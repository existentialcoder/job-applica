<script setup lang="ts">
import { computed } from 'vue';
import { RouterLink } from 'vue-router';
import { Button } from '@/components/ui/button';
import { ONBOARDING_STEPS } from '@/lib/constants';
import { useAuthStore } from '@/stores/auth';
import { useOnboardingStore } from '@/stores/onboarding';

const authStore = useAuthStore();
const onboardingStore = useOnboardingStore();
const greeting = computed(() =>
  authStore.user?.first_name ? `Welcome, ${authStore.user.first_name}` : 'Welcome'
);
</script>

<template>
  <div class="flex flex-col gap-5">
    <div class="flex flex-col items-center text-center gap-2 pt-6">
      <h1 class="text-[28px] font-bold tracking-tight">{{ greeting }}</h1>
      <p class="text-[15px] text-muted-foreground">
        Let's get your job search set up with three quick steps.
      </p>
    </div>
    <ol class="mx-auto mt-2 w-full max-w-[520px] flex flex-col gap-2.5">
      <li
        v-for="step in ONBOARDING_STEPS"
        :key="step.title"
        class="flex items-center gap-3.5 px-4 py-3.5 rounded-xl border border-border bg-card"
      >
        <span class="size-10 shrink-0 rounded-[10px] bg-primary/10 text-primary flex items-center justify-center">
          <Icon :name="step.icon" :size="18" :stroke-width="2" />
        </span>
        <span class="flex flex-col gap-0.5">
          <span class="text-sm font-semibold">{{ step.title }}</span>
          <span class="text-[13px] text-muted-foreground">{{ step.hint }}</span>
        </span>
      </li>
    </ol>
    <div class="flex flex-col items-center gap-2.5 pt-2">
      <Button class="h-11" @click="onboardingStore.go('upload')">
          Get started
          <Icon name="ArrowRight" :size="16" :stroke-width="2" default-class="ml-2" />
      </Button>
      <RouterLink to="/home" class="text-sm text-muted-foreground hover:text-foreground">Skip</RouterLink>
    </div>
  </div>
</template>
