<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogTitle } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import type { ResumeData, SkillData } from '@/lib/types';
import { useAppStore } from '@/stores/app';
import { useResumesStore } from '@/stores/resumes';
import { useSkillStore } from '@/stores/skills';

const appStore = useAppStore();
onMounted(() => {
  appStore.setBreadcrumbs([{ label: 'Resumes' }]);
  loadData();
});

const skillsStore = useSkillStore();
const resumesStore = useResumesStore();

const preview = ref<ResumeData | null>(null);
const previewOpen = ref(false);

const skillSearch = ref('');
const skillsLoaded = ref(false);
const dropdownOpen = ref(false);
const addingId = ref<number | null>(null);
const removingId = ref<number | null>(null);

const filteredSkills = computed(() => {
  const q = skillSearch.value.toLowerCase().trim();
  const addedIds = new Set(skillsStore.userSkills.map((s) => s.id));
  return skillsStore.skills.filter(
    (s) =>
      !addedIds.has(s.id) &&
      (!q || s.label.toLowerCase().includes(q) || s.name.toLowerCase().includes(q))
  );
});

async function loadData() {
  await Promise.all([
    resumesStore.fetch(),
    skillsStore.fetch()
  ]);
}

async function handleFileChange(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0];
  if (!file) {
    return;
  }
  try {
    await resumesStore.addResume(file);
  } catch(ex) {
    //no-op
  } finally {
    (e.target as HTMLInputElement).value = '';
  }
}

function viewResume(resume: ResumeData) {
  preview.value = resume;
  previewOpen.value = true;
}

// ── Skill actions ─────────────────────────────────────────────────────────────
async function addSkill(skill: SkillData) {
  addingId.value = skill.id;
  const ok = await skillsStore.addUserSkill(skill.id);
  if (ok) skillSearch.value = '';
  addingId.value = null;
}

async function removeSkill(skillId: number) {
  removingId.value = skillId;
  await skillsStore.removeUserSkill(skillId);
  removingId.value = null;
}

// ── Helpers ───────────────────────────────────────────────────────────────────
function formatSize(bytes: number | null) {
  if (!bytes) return '—';
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

function formatDate(iso: string | null) {
  if (!iso) return '';
  return new Date(iso).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
}
</script>

<template>
  <div class="p-6 flex flex-col gap-6">
    <!-- ── Resumes section ──────────────────────────────────────────────────── -->
    <div class="rounded-xl border bg-card">
      <!-- Section header -->
      <div class="flex items-center justify-between p-6 border-b">
        <div>
          <p class="text-sm font-semibold">Resumes</p>
          <p class="text-xs text-muted-foreground mt-0.5">
            Upload and organize your resumes tailored to each job application.
          </p>
        </div>
        <label>
          <input
            type="file"
            class="sr-only"
            accept=".pdf,.doc,.docx"
            :disabled="resumesStore.newResumeUpload"
            @change="handleFileChange"
          />
          <Button as="span" size="sm" :disabled="resumesStore.newResumeUpload" class="cursor-pointer">
            <Icon name="Upload" :size="14" :stroke-width="2" default-class="mr-1.5" />
            {{ resumesStore.newResumeUpload ? 'Uploading…' : 'Upload CV' }}
          </Button>
        </label>
      </div>

      <!-- Empty state -->
      <div
        v-if="resumesStore.loaded && !resumesStore.resumes.length"
        class="flex flex-col items-center justify-center py-12 text-center"
      >
        <div class="w-12 h-12 rounded-xl bg-muted flex items-center justify-center mb-3">
          <Icon name="FileText" :size="24" default-class="text-muted-foreground" />
        </div>
        <p class="text-sm font-medium">No CVs yet</p>
        <p class="text-xs text-muted-foreground mt-1">
          Upload a PDF or Word document to get started
        </p>
      </div>

      <!-- Resume rows -->
      <div v-else class="divide-y divide-border">
        <div v-for="resume in resumesStore.resumes" :key="resume.id" class="flex items-center gap-4 px-6 py-4">
          <div
            class="w-9 h-9 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0"
          >
            <Icon name="FileText" :size="16" default-class="text-primary" />
          </div>

          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium truncate">{{ resume.original_name }}</p>
            <p class="text-xs text-muted-foreground mt-0.5">
              {{ formatSize(resume.file_size) }} · {{ formatDate(resume.created_at) }}
            </p>
          </div>

          <button
            :class="[
              'flex-shrink-0 text-xs font-medium px-2 py-0.5 rounded-full border transition-colors',
              resume.is_default
                ? 'bg-primary/10 text-primary border-primary/20'
                : 'border-border text-muted-foreground hover:border-primary/30 hover:text-foreground'
            ]"
            @click="resumesStore.setDefault(resume.id)"
          >
            {{ resume.is_default ? 'Default' : 'Set default' }}
          </button>

          <div class="flex items-center gap-1 flex-shrink-0">
            <Button
              variant="ghost"
              size="icon"
              class="h-8 w-8"
              title="View"
              @click="viewResume(resume)"
            >
              <Icon name="Eye" :size="16" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              class="h-8 w-8 text-destructive hover:text-destructive hover:bg-destructive/10"
              title="Delete"
              @click="resumesStore.deleteResume(resume.id)"
            >
              <Icon name="Trash2" :size="16" />
            </Button>
          </div>
        </div>
      </div>
    </div>

    <div class="rounded-xl border bg-card p-6 space-y-5">
      <div>
        <p class="text-sm font-semibold">Skills</p>
        <p class="text-xs text-muted-foreground mt-0.5">
          Auto-extracted from the resumes you uploaded. Know where you stand.
        </p>
      </div>

      <div class="min-h-[2rem]">
        <div v-if="skillsStore.userSkills.length" class="flex flex-wrap gap-2">
          <span
            v-for="skill in skillsStore.userSkills"
            :key="skill.id"
            class="flex items-center gap-1.5 bg-primary/10 text-primary text-xs font-medium px-2.5 py-1 rounded-full transition-opacity"
            :class="removingId === skill.id ? 'opacity-40' : ''"
          >
            <img
              v-if="skill.logo_url"
              :src="skill.logo_url"
              class="w-3.5 h-3.5 rounded-sm object-contain"
            />
            {{ skill.label }}
            <button
              :disabled="removingId === skill.id"
              class="ml-0.5 w-3.5 h-3.5 flex items-center justify-center rounded-full opacity-50 hover:opacity-100 transition-all"
              @click="removeSkill(skill.id)"
            >
              <Icon name="X" :size="10" :stroke-width="3" />
            </button>
          </span>
        </div>
        <p v-else-if="skillsLoaded" class="text-sm text-muted-foreground">
          No skills yet. Upload a CV to auto-extract, or search below to add manually.
        </p>
      </div>

      <div class="relative">
        <div class="relative">
          <Icon
            name="Search"
            :size="14"
            :stroke-width="2"
            default-class="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground pointer-events-none"
          />
          <Input
            v-model="skillSearch"
            placeholder="Search skills to add…"
            class="pl-8"
            @focus="dropdownOpen = true"
            @blur="
              setTimeout(() => {
                dropdownOpen = false
              }, 120)
            "
          />
          <span
            v-if="skillSearch"
            class="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-muted-foreground"
          >
            {{ filteredSkills.length }} result{{ filteredSkills.length !== 1 ? 's' : '' }}
          </span>
        </div>

        <div
          v-if="dropdownOpen && skillsLoaded"
          class="absolute z-50 top-full mt-1 w-full rounded-md border bg-popover shadow-lg overflow-hidden"
        >
          <div class="max-h-60 overflow-y-auto">
            <div
              v-if="filteredSkills.length === 0 && skillSearch"
              class="px-3 py-2.5 text-xs text-muted-foreground"
            >
              No skills match "{{ skillSearch }}"
            </div>
            <div
              v-else-if="filteredSkills.length === 0"
              class="px-3 py-2.5 text-xs text-muted-foreground"
            >
              All skills have been added
            </div>
            <button
              v-for="skill in filteredSkills.slice(0, 60)"
              :key="skill.id"
              :disabled="addingId === skill.id"
              class="w-full flex items-center gap-2.5 px-3 py-2 text-sm hover:bg-accent transition-colors text-left"
              @mousedown.prevent="addSkill(skill)"
            >
              <img
                v-if="skill.logo_url"
                :src="skill.logo_url"
                class="w-4 h-4 rounded-sm object-contain flex-shrink-0"
              />
              <span v-else class="w-4 h-4 rounded-sm bg-muted flex-shrink-0" />
              <span class="truncate">{{ skill.label }}</span>
              <Icon
                v-if="addingId === skill.id"
                name="LoaderCircle"
                :size="14"
                default-class="ml-auto animate-spin text-muted-foreground flex-shrink-0"
              />
              <Icon
                v-else
                name="Plus"
                :size="14"
                :stroke-width="2"
                default-class="ml-auto text-muted-foreground/40 flex-shrink-0"
              />
            </button>
            <div
              v-if="filteredSkills.length > 60"
              class="px-3 py-1.5 text-xs text-muted-foreground border-t"
            >
              Showing 60 of {{ filteredSkills.length }} — type to narrow
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <Dialog :open="previewOpen" @update:open="previewOpen = $event">
    <DialogContent class="max-w-[75vw] w-[75vw] h-[90vh] !grid-rows-[auto_1fr] overflow-hidden p-0">
      <div class="flex items-center px-5 pt-5 pb-3 border-b">
        <DialogTitle class="text-sm font-semibold truncate">{{
          preview?.original_name
        }}</DialogTitle>
      </div>
      <iframe v-if="preview" :src="preview.url" class="w-full border-0 h-full" />
    </DialogContent>
  </Dialog>
</template>
