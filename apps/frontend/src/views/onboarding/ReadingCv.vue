<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue';
import { useOnboardingStore } from '@/stores/onboarding';
import { useResumesStore } from '@/stores/resumes';

const POLL_MS = 1500;
// The PRD targets 15 s at p95; well past that, stop waiting and let the user fill the form in.
const GIVE_UP_MS = 45_000;
const STAGES = ['Uploading your CV', 'Fetching details', 'Filling in your profile'];
// Which stage each extraction status is on; the upload is already done when this screen opens.
const STAGE_OF: Record<string, number> = { pending: 1, filling: 2, done: 3 };

const resumesStore = useResumesStore();
const onboardingStore = useOnboardingStore();
// Uploading or replacing makes the new CV the current one.
const resumeId = resumesStore.current?.id;
const fileName = ref('');
const stage = ref(1);
let timer: ReturnType<typeof setTimeout> | undefined;
const startedAt = Date.now();

// Halfway into the active stage, full once everything is done.
const percent = computed(() => (stage.value >= STAGES.length ? 100 : Math.round(((stage.value + 0.5) / STAGES.length) * 100)));

async function poll() {
  const resume = resumeId ? await resumesStore.get(resumeId).catch(() => null) : null;
  fileName.value = resume?.original_name ?? fileName.value;
  const status = resume?.extraction ?? '';
  if (status in STAGE_OF) stage.value = STAGE_OF[status];
  if (status === 'done') {
    // Let the finished bar and ticks show for a moment before moving on.
    timer = setTimeout(() => onboardingStore.go('profile'), 600);
  } else if ((status === 'pending' || status === 'filling') && Date.now() - startedAt < GIVE_UP_MS) {
    timer = setTimeout(poll, POLL_MS);
  } else {
    onboardingStore.go('profile');
  }
}

onMounted(poll);
onBeforeUnmount(() => clearTimeout(timer));
</script>

<template>
  <div class="flex flex-col gap-5">
    <div>
      <h1 class="text-2xl font-bold tracking-tight">Reading your CV…</h1>
      <p class="mt-1 text-sm text-muted-foreground">
        This usually takes a few seconds. You can skip and come back later.
      </p>
    </div>
    <div class="rounded-xl border border-border bg-card p-6 flex flex-col gap-6">
      <div class="flex items-center gap-3 px-3.5 py-3 rounded-lg border border-border">
        <span class="size-9 shrink-0 rounded-lg bg-primary/10 text-primary flex items-center justify-center">
          <Icon name="FileText" :size="16" :stroke-width="2" />
        </span>
        <span class="flex flex-col min-w-0">
          <span class="text-sm font-medium truncate">{{ fileName || 'Your CV' }}</span>
          <span class="text-xs text-muted-foreground">Uploaded just now</span>
        </span>
      </div>

      <div
        role="progressbar"
        aria-label="Reading your CV"
        :aria-valuenow="percent"
        aria-valuemin="0"
        aria-valuemax="100"
        class="h-1.5 rounded-full bg-muted overflow-hidden"
      >
        <div class="h-full rounded-full bg-primary transition-[width] duration-500 ease-out" :style="{ width: `${percent}%` }" />
      </div>

      <ol class="flex flex-col gap-4" aria-live="polite">
        <li
          v-for="(label, i) in STAGES"
          :key="label"
          class="flex items-center gap-3 text-sm font-medium"
          :class="i > stage ? 'text-muted-foreground' : 'text-foreground'"
          :aria-current="i === stage ? 'step' : undefined"
        >
          <span
            v-if="i < stage"
            class="size-5 shrink-0 rounded-full bg-primary text-primary-foreground flex items-center justify-center"
          >
            <Icon name="Check" :size="12" :stroke-width="3" />
          </span>
          <Icon
            v-else-if="i === stage"
            name="LoaderCircle"
            :size="20"
            :stroke-width="2"
            default-class="shrink-0 text-primary motion-safe:animate-spin"
          />
          <span v-else class="size-5 shrink-0 rounded-full border-2 border-border" />
          {{ label }}
        </li>
      </ol>
    </div>
  </div>
</template>
