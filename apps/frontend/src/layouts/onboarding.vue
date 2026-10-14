<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import AppLogo from '@/components/core/AppLogo.vue';
import { Button } from '@/components/ui/button';
import { ONBOARDING_STEPS } from '@/lib/constants';
import { toast } from '@/lib/toast';
import { type OnboardingView, useOnboardingStore } from '@/stores/onboarding';
import Finishing from '@/views/onboarding/Finishing.vue';
import JobPreferences from '@/views/onboarding/JobPreferences.vue';
import ReadingCv from '@/views/onboarding/ReadingCv.vue';
import ReviewProfile from '@/views/onboarding/ReviewProfile.vue';
import UploadCv from '@/views/onboarding/UploadCv.vue';
import Welcome from '@/views/onboarding/Welcome.vue';

const SCREENS = {
  welcome: Welcome,
  upload: UploadCv,
  reading: ReadingCv,
  profile: ReviewProfile,
  preferences: JobPreferences,
  finishing: Finishing
};
const STEP_OF: Partial<Record<OnboardingView, number>> = { upload: 1, reading: 2, profile: 2, preferences: 3 };
const BACK_TO: Partial<Record<OnboardingView, 'upload' | 'profile'>> = { profile: 'upload', preferences: 'profile' };

const onboardingStore = useOnboardingStore();
const router = useRouter();
const ready = ref(false);
const skipping = ref(false);
const current = computed(() => STEP_OF[onboardingStore.view]);
const back = computed(() => BACK_TO[onboardingStore.view]);


async function skip() {
  skipping.value = true;
  try {
    await onboardingStore.skip();
    if (onboardingStore.view !== 'finishing') router.push('/home');
  } catch {
    toast.error("Couldn't skip this step. Try again.");
  } finally {
    skipping.value = false;
  }
}

onMounted(async () => {
  await onboardingStore.start();
  ready.value = true;
});
</script>

<template>
  <div class="min-h-screen flex flex-col bg-background">
    <header
      class="sticky top-0 z-40 min-h-16 shrink-0 flex flex-wrap items-center justify-between gap-x-4 gap-y-2 py-3 px-4 lg:px-8 border-b border-border bg-card"
    >
      <AppLogo />
      <ol
        v-if="current"
        :aria-label="`Setup progress, step ${current} of ${ONBOARDING_STEPS.length}`"
        class="hidden md:flex items-center gap-3"
      >
        <template v-for="(step, i) in ONBOARDING_STEPS" :key="step.view">
          <li
            v-if="i > 0"
            aria-hidden="true"
            class="w-12 h-0.5 rounded"
            :class="i < current ? 'bg-primary' : 'bg-border'"
          />
          <li>
            <button
              type="button"
              class="flex items-center gap-2 text-sm rounded-md px-1.5 py-1 -mx-1.5 hover:bg-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              :class="i + 1 > current ? 'font-medium text-muted-foreground' : 'font-semibold text-foreground'"
              :aria-current="i + 1 === current ? 'step' : undefined"
              @click="onboardingStore.go(step.view)"
            >
              <span
                v-if="i + 1 < current"
                class="size-6 rounded-full bg-primary text-primary-foreground flex items-center justify-center"
              >
                <Icon name="Check" :size="14" :stroke-width="2" />
              </span>
              <span
                v-else
                class="size-6 rounded-full flex items-center justify-center text-xs font-bold"
                :class="i + 1 === current ? 'border-2 border-primary text-primary' : 'border border-border'"
              >
                {{ i + 1 }}
              </span>
              {{ step.title }}
            </button>
          </li>
        </template>
      </ol>
      <span v-if="current" class="text-sm text-muted-foreground md:hidden">Step {{ current }} of {{ ONBOARDING_STEPS.length }}</span>
      <div v-if="current" class="flex w-full items-center justify-end gap-2 md:w-auto">
        <Button v-if="back" variant="ghost" @click="onboardingStore.go(back)">Back</Button>
        <Button variant="outline" :disabled="skipping" @click="skip">Skip</Button>
        <!-- Each screen teleports its main action here, so it stays in reach while scrolling. -->
        <div id="onboarding-actions" class="contents" />
      </div>
    </header>
    <main class="flex-1 flex justify-center px-4 py-10 lg:px-8">
      <div class="w-full max-w-[880px]">
        <component :is="SCREENS[onboardingStore.view]" v-if="ready" :key="onboardingStore.view" />
      </div>
    </main>
  </div>
</template>
