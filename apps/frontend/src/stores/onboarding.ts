import { defineStore } from 'pinia';
import { computed, ref } from 'vue';
import dataservice from '@/lib/dataservice';
import type { Onboarding } from '@/lib/dataservice';
import { useResumesStore } from '@/stores/resumes';

/** A setup screen: the saved steps, plus the screens shown while a CV is being read and once setup is done. */
export type OnboardingView = Onboarding['step'] | 'reading' | 'finishing';

export const useOnboardingStore = defineStore('onboarding', () => {
  // null: no setup record (an account from before setup existed) or not loaded yet.
  const onboarding = ref<Onboarding | null>(null);
  const view = ref<OnboardingView>('welcome');

  /** Where an unfinished setup resumes, or null when there's nothing to finish. */
  const setupPath = computed(() => (onboarding.value && !onboarding.value.completed_at ? '/onboarding' : null));

  async function fetch() {
    onboarding.value = await dataservice.getOnboarding().catch(() => null);
  }

  async function landingPath(fallback: string): Promise<string> {
    await fetch();
    return setupPath.value ?? fallback;
  }

  /** Pick the screen to open: the saved step, or the reading screen while the CV is still being read. */
  async function start() {
    const resumesStore = useResumesStore();
    await Promise.all([fetch(), resumesStore.refresh()]);
    const step = onboarding.value?.step ?? 'welcome';
    const reading = ['pending', 'filling'].includes(resumesStore.current?.extraction ?? '');
    view.value = step === 'profile' && reading ? 'reading' : step;
  }

  async function updateStep(step: Onboarding['step'], opts: { skipped?: boolean; complete?: boolean } = {}) {
    await dataservice.updateOnboardingStep(step, opts);
    if (onboarding.value) {
      onboarding.value = {
        ...onboarding.value,
        step,
        completed_at: opts.complete ? new Date().toISOString() : onboarding.value.completed_at
      };
    }
  }

  /** Show a screen and save its step, so a reload or the next sign-in opens it again. */
  async function go(next: Exclude<OnboardingView, 'finishing'>) {
    view.value = next;
    const step = next === 'reading' ? 'profile' : next;
    if (onboarding.value?.step !== step) {
      await updateStep(step);
    }
  }

  async function finish(opts: { skipped?: boolean } = {}) {
    await updateStep('preferences', { ...opts, complete: true });
    view.value = 'finishing';
  }

  /** Leave setup for now. Skipping the last step finishes it, so sign-in stops opening setup. */
  async function skip() {
    if (view.value === 'preferences') await finish({ skipped: true });
  }

  return { onboarding, view, setupPath, fetch, landingPath, start, updateStep, go, finish, skip };
});
