<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { Button } from '@/components/ui/button';
import { ONBOARDING_STEP } from '@/lib/constants';
import type { ResumeData } from '@/lib/types';
import { useOnboardingStore } from '@/stores/onboarding';
import { useResumesStore } from '@/stores/resumes';

const resumesStore = useResumesStore();
const onboardingStore = useOnboardingStore();
// The CV already uploaded during setup, if the user came back to this step.
const current = computed(() => resumesStore.current);
const file = ref<File | null>(null);
const dragging = ref(false);
const uploading = ref(false);
const loading = ref(true);
const error = ref('');

onMounted(async () => {
  await resumesStore.fetch();
  loading.value = false;
});

function pick(files: FileList | null | undefined) {
  if (!files?.length) return;
  file.value = files[0];
  error.value = '';
}

function onDrop(e: DragEvent) {
  dragging.value = false;
  pick(e.dataTransfer?.files);
}

const uploadedOn = (r: ResumeData) =>
  new Date(r.created_at).toLocaleDateString(undefined, { day: 'numeric', month: 'short', year: 'numeric' });

async function onContinue() {
  if (!file.value && current.value) {
    // Keeping the CV: wait for its extraction if it's still running, else go straight to the profile.
    await onboardingStore.go(['pending', 'filling'].includes(current.value.extraction ?? '') ? 'reading' : 'profile');
    return;
  }
  if (!file.value) return;
  uploading.value = true;
  try {
    if (current.value) await resumesStore.replace(current.value.id, file.value);
    else await resumesStore.upload(file.value);
    await onboardingStore.go('reading');
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Upload failed';
  } finally {
    uploading.value = false;
  }
}
</script>

<template>
  <div class="flex flex-col gap-5">
    <div>
      <h1 class="text-2xl font-bold tracking-tight">{{ ONBOARDING_STEP.upload.title }}</h1>
      <p class="mt-1 text-sm text-muted-foreground">{{ ONBOARDING_STEP.upload.hint }}</p>
    </div>
    <div v-if="!loading" class="rounded-xl border border-border bg-card p-6 flex flex-col gap-4">
      <div v-if="current && !file" class="flex flex-wrap items-center gap-3 px-4 py-3.5 rounded-lg border border-border">
        <span class="size-10 shrink-0 rounded-lg bg-primary/10 text-primary flex items-center justify-center">
          <Icon name="FileText" :size="18" :stroke-width="2" />
        </span>
        <span class="flex-1 min-w-[160px] flex flex-col min-w-0">
          <span class="text-sm font-medium truncate">{{ current.original_name }}</span>
          <span class="text-xs text-muted-foreground">Uploaded {{ uploadedOn(current) }}</span>
        </span>
        <Button variant="outline" as-child>
          <label class="cursor-pointer focus-within:ring-2 focus-within:ring-ring">
            <input
              type="file"
              accept=".pdf,.docx"
              class="sr-only"
              @change="pick(($event.target as HTMLInputElement).files)"
            />
            <Icon name="RefreshCw" :size="16" :stroke-width="2" default-class="mr-2" />
            Replace
          </label>
        </Button>
      </div>

      <template v-else>
        <label
          class="flex flex-col items-center gap-3 px-6 py-14 rounded-xl border-2 border-dashed text-center cursor-pointer
            focus-within:ring-2 focus-within:ring-ring"
          :class="dragging ? 'border-primary bg-primary/5' : 'border-border'"
          @dragover.prevent="dragging = true"
          @dragleave="dragging = false"
          @drop.prevent="onDrop"
        >
          <input
            type="file"
            accept=".pdf,.docx"
            class="sr-only"
            @change="pick(($event.target as HTMLInputElement).files)"
          />
          <span class="size-12 rounded-xl bg-primary/10 text-primary flex items-center justify-center">
            <Icon :name="file ? 'FileText' : 'Upload'" :size="24" :stroke-width="2" />
          </span>
          <span v-if="file" class="text-[15px] font-semibold">{{ file.name }}</span>
          <span v-else class="text-[15px] font-semibold">
            Drop your CV here, or <span class="text-primary underline">browse</span>
          </span>
          <span class="text-[13px] text-muted-foreground">
            {{ file ? 'Choose a different file' : 'PDF or Word, up to 5 MB' }}
          </span>
        </label>
        <p v-if="current && file" class="flex flex-wrap items-center gap-x-2 text-[13px] text-muted-foreground">
          This replaces {{ current.original_name }}, and your profile is filled in again from the new CV.
          <button type="button" class="text-primary underline" @click="file = null">Keep the current CV</button>
        </p>
      </template>
      <p v-if="error" role="alert" class="text-sm text-destructive">{{ error }}</p>
    </div>
    <Teleport to="#onboarding-actions">
      <Button :disabled="loading || (!file && !current) || uploading" @click="onContinue">
        {{ uploading ? 'Uploading…' : 'Continue' }}
        <Icon name="ArrowRight" :size="16" :stroke-width="2" default-class="ml-2" />
      </Button>
    </Teleport>
  </div>
</template>
