<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Dialog, DialogContent, DialogTitle } from '@/components/ui/dialog';
import { toast } from '@/lib/toast';
import { useAppStore } from '@/stores/app';
import dataservice from '@/lib/dataservice';
import type { ResumeData, SkillData } from '@/lib/types';

const appStore = useAppStore();
onMounted(() => {
  appStore.setBreadcrumbs([{ label: 'Resumes' }]);
  loadData();
});

// ── Resumes ───────────────────────────────────────────────────────────────────
const resumes     = ref<ResumeData[]>([]);
const loaded      = ref(false);
const uploading   = ref(false);
const preview     = ref<ResumeData | null>(null);
const previewOpen = ref(false);

// ── Skills ────────────────────────────────────────────────────────────────────
const userSkills   = ref<SkillData[]>([]);
const allSkills    = ref<SkillData[]>([]);
const skillSearch  = ref('');
const skillsLoaded = ref(false);
const dropdownOpen = ref(false);
const addingId     = ref<number | null>(null);
const removingId   = ref<number | null>(null);

const filteredSkills = computed(() => {
  const q = skillSearch.value.toLowerCase().trim();
  const addedIds = new Set(userSkills.value.map(s => s.id));
  return allSkills.value.filter(
    s => !addedIds.has(s.id) && (!q || s.label.toLowerCase().includes(q) || s.name.toLowerCase().includes(q))
  );
});

async function loadData() {
  [resumes.value, userSkills.value, allSkills.value] = await Promise.all([
    dataservice.getResumes(),
    dataservice.getUserSkills(),
    dataservice.getSkills(),
  ]);
  loaded.value = true;
  skillsLoaded.value = true;
}

// ── Resume actions ────────────────────────────────────────────────────────────
async function handleFileChange(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0];
  if (!file) return;
  uploading.value = true;
  try {
    const resume = await dataservice.uploadResume(file);
    resumes.value.unshift(resume);
    toast.success('CV uploaded — skills are being extracted in the background');
  } catch (err: any) {
    toast.error(err.message ?? 'Upload failed');
  } finally {
    uploading.value = false;
    (e.target as HTMLInputElement).value = '';
  }
}

async function deleteResume(id: number) {
  try {
    await dataservice.deleteResume(id);
    resumes.value = resumes.value.filter(r => r.id !== id);
    toast.success('CV deleted');
  } catch {
    toast.error('Failed to delete CV');
  }
}

async function setDefault(resumeId: number) {
  try {
    await dataservice.setDefaultResume(resumeId);
    resumes.value = resumes.value.map(r => ({ ...r, is_default: r.id === resumeId }));
  } catch {
    toast.error('Failed to set default');
  }
}

function viewResume(resume: ResumeData) {
  preview.value = resume;
  previewOpen.value = true;
}

// ── Skill actions ─────────────────────────────────────────────────────────────
async function addSkill(skill: SkillData) {
  addingId.value = skill.id;
  try {
    userSkills.value = await dataservice.addUserSkill(skill.id);
    skillSearch.value = '';
  } catch {
    toast.error('Failed to add skill');
  } finally {
    addingId.value = null;
  }
}

async function removeSkill(skillId: number) {
  removingId.value = skillId;
  try {
    userSkills.value = await dataservice.removeUserSkill(skillId);
  } catch {
    toast.error('Failed to remove skill');
  } finally {
    removingId.value = null;
  }
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
  return new Date(iso).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
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
          <p class="text-xs text-muted-foreground mt-0.5">Upload and organize your resumes tailored to each job application.</p>
        </div>
        <label>
          <input type="file" class="sr-only" accept=".pdf,.doc,.docx" :disabled="uploading" @change="handleFileChange" />
          <Button as="span" size="sm" :disabled="uploading" class="cursor-pointer">
            <svg class="w-3.5 h-3.5 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"/>
            </svg>
            {{ uploading ? 'Uploading…' : 'Upload CV' }}
          </Button>
        </label>
      </div>

      <!-- Empty state -->
      <div v-if="loaded && !resumes.length" class="flex flex-col items-center justify-center py-12 text-center">
        <div class="w-12 h-12 rounded-xl bg-muted flex items-center justify-center mb-3">
          <svg class="w-6 h-6 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
          </svg>
        </div>
        <p class="text-sm font-medium">No CVs yet</p>
        <p class="text-xs text-muted-foreground mt-1">Upload a PDF or Word document to get started</p>
      </div>

      <!-- Resume rows -->
      <div v-else class="divide-y divide-border">
        <div
          v-for="resume in resumes"
          :key="resume.id"
          class="flex items-center gap-4 px-6 py-4"
        >
          <div class="w-9 h-9 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
            <svg class="w-4 h-4 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
            </svg>
          </div>

          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium truncate">{{ resume.original_name }}</p>
            <p class="text-xs text-muted-foreground mt-0.5">{{ formatSize(resume.file_size) }} · {{ formatDate(resume.created_at) }}</p>
          </div>

          <button
            :class="[
              'flex-shrink-0 text-xs font-medium px-2 py-0.5 rounded-full border transition-colors',
              resume.is_default
                ? 'bg-primary/10 text-primary border-primary/20'
                : 'border-border text-muted-foreground hover:border-primary/30 hover:text-foreground',
            ]"
            @click="setDefault(resume.id)"
          >
            {{ resume.is_default ? 'Default' : 'Set default' }}
          </button>

          <div class="flex items-center gap-1 flex-shrink-0">
            <Button variant="ghost" size="icon" class="h-8 w-8" title="View" @click="viewResume(resume)">
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z"/>
                <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
              </svg>
            </Button>
            <Button variant="ghost" size="icon" class="h-8 w-8 text-destructive hover:text-destructive hover:bg-destructive/10" title="Delete" @click="deleteResume(resume.id)">
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0"/>
              </svg>
            </Button>
          </div>
        </div>
      </div>
    </div>

    <!-- ── Skills section ───────────────────────────────────────────────────── -->
    <div class="rounded-xl border bg-card p-6 space-y-5">
      <div>
        <p class="text-sm font-semibold">Skills</p>
        <p class="text-xs text-muted-foreground mt-0.5">Auto-extracted from the resumes you uploaded. Know where you stand.</p>
      </div>

      <!-- Chip list -->
      <div class="min-h-[2rem]">
        <div v-if="userSkills.length" class="flex flex-wrap gap-2">
          <span
            v-for="skill in userSkills"
            :key="skill.id"
            class="flex items-center gap-1.5 bg-primary/10 text-primary text-xs font-medium px-2.5 py-1 rounded-full transition-opacity"
            :class="removingId === skill.id ? 'opacity-40' : ''"
          >
            <img v-if="skill.logo_url" :src="skill.logo_url" class="w-3.5 h-3.5 rounded-sm object-contain" />
            {{ skill.label }}
            <button
              :disabled="removingId === skill.id"
              class="ml-0.5 w-3.5 h-3.5 flex items-center justify-center rounded-full opacity-50 hover:opacity-100 transition-all"
              @click="removeSkill(skill.id)"
            >
              <svg class="w-2.5 h-2.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </span>
        </div>
        <p v-else-if="skillsLoaded" class="text-sm text-muted-foreground">No skills yet. Upload a CV to auto-extract, or search below to add manually.</p>
      </div>

      <!-- Search / add -->
      <div class="relative">
        <div class="relative">
          <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground pointer-events-none" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-4.35-4.35M17 11A6 6 0 105 11a6 6 0 0012 0z" />
          </svg>
          <Input
            v-model="skillSearch"
            placeholder="Search skills to add…"
            class="pl-8"
            @focus="dropdownOpen = true"
            @blur="setTimeout(() => { dropdownOpen = false }, 120)"
          />
          <span v-if="skillSearch" class="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-muted-foreground">
            {{ filteredSkills.length }} result{{ filteredSkills.length !== 1 ? 's' : '' }}
          </span>
        </div>

        <div v-if="dropdownOpen && skillsLoaded" class="absolute z-50 top-full mt-1 w-full rounded-md border bg-popover shadow-lg overflow-hidden">
          <div class="max-h-60 overflow-y-auto">
            <div v-if="filteredSkills.length === 0 && skillSearch" class="px-3 py-2.5 text-xs text-muted-foreground">No skills match "{{ skillSearch }}"</div>
            <div v-else-if="filteredSkills.length === 0" class="px-3 py-2.5 text-xs text-muted-foreground">All skills have been added</div>
            <button
              v-for="skill in filteredSkills.slice(0, 60)"
              :key="skill.id"
              :disabled="addingId === skill.id"
              class="w-full flex items-center gap-2.5 px-3 py-2 text-sm hover:bg-accent transition-colors text-left"
              @mousedown.prevent="addSkill(skill)"
            >
              <img v-if="skill.logo_url" :src="skill.logo_url" class="w-4 h-4 rounded-sm object-contain flex-shrink-0" />
              <span v-else class="w-4 h-4 rounded-sm bg-muted flex-shrink-0" />
              <span class="truncate">{{ skill.label }}</span>
              <svg v-if="addingId === skill.id" class="ml-auto w-3.5 h-3.5 animate-spin text-muted-foreground flex-shrink-0" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
              </svg>
              <svg v-else class="ml-auto w-3.5 h-3.5 text-muted-foreground/40 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4" />
              </svg>
            </button>
            <div v-if="filteredSkills.length > 60" class="px-3 py-1.5 text-xs text-muted-foreground border-t">Showing 60 of {{ filteredSkills.length }} — type to narrow</div>
          </div>
        </div>
      </div>
    </div>

  </div>

  <!-- Resume preview dialog -->
  <Dialog :open="previewOpen" @update:open="previewOpen = $event">
    <DialogContent class="max-w-[75vw] w-[75vw] h-[90vh] !grid-rows-[auto_1fr] overflow-hidden p-0">
      <div class="flex items-center px-5 pt-5 pb-3 border-b">
        <DialogTitle class="text-sm font-semibold truncate">{{ preview?.original_name }}</DialogTitle>
      </div>
      <iframe v-if="preview" :src="preview.url" class="w-full border-0 h-full" />
    </DialogContent>
  </Dialog>
</template>
