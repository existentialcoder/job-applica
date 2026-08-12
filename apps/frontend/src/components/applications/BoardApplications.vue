<script setup lang="ts">
import { MapPin } from 'lucide-vue-next';
import {
  ScrollAreaRoot,
  ScrollAreaViewport,
  ScrollAreaScrollbar,
  ScrollAreaThumb,
  ScrollAreaCorner
} from 'radix-vue';
import { computed, ref, nextTick } from 'vue';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger
} from '@/components/ui/dropdown-menu';
import { DEFAULT_COMPANY_LOGO_URL, MANDATORY_STAGE_KEYS } from '@/lib/constants';
import type { JobData, StageData } from '@/lib/types';

const DEFAULT_COLUMNS: StageData[] = [
  { key: 'Saved', label: 'Saved', color: 'bg-slate-500' },
  { key: 'Applied', label: 'Applied', color: 'bg-blue-500' },
  { key: 'Phone Screen', label: 'Phone Screen', color: 'bg-amber-500' },
  { key: 'Interview', label: 'Interview', color: 'bg-amber-500' },
  { key: 'Technical', label: 'Technical', color: 'bg-orange-500' },
  { key: 'Offer', label: 'Offer', color: 'bg-emerald-500' },
  { key: 'Rejected', label: 'Rejected', color: 'bg-red-500' },
  { key: 'Withdrawn', label: 'Withdrawn', color: 'bg-zinc-400' }
];

const props = defineProps<{
  jobs: JobData[]
  stages?: StageData[]
}>();

const emit = defineEmits<{
  (e: 'edit', job: JobData): void
  (e: 'status-change', jobId: number, status: string): void
  (e: 'delete', jobId: number): void
  (e: 'remove-stage', key: string): void
  (e: 'add-stage', stage: StageData): void
  (e: 'update-stage', payload: { oldKey: string; stage: StageData }): void
  (e: 'add-job', payload: { title: string; company_name?: string; status: string }): void
}>();

const STAGE_COLORS = [
  'bg-slate-500',
  'bg-blue-500',
  'bg-violet-500',
  'bg-emerald-500',
  'bg-amber-500',
  'bg-rose-500',
  'bg-orange-500',
  'bg-cyan-500',
  'bg-pink-500',
  'bg-teal-500'
];

// ── Add stage state ───────────────────────────────────────────────────────────
const showAddStage = ref(false);
const newStageName = ref('');
const addStageInputRef = ref<HTMLInputElement | null>(null);

// ── Stage rename state ────────────────────────────────────────────────────────
const editingStageKey = ref<string | null>(null);
const editingStageLabel = ref('');

// ── Quick-add card state ──────────────────────────────────────────────────────
const addingJobForStatus = ref<string | null>(null);
const quickAddTitle = ref('');
const quickAddCompany = ref('');
const quickTitleInputRef = ref<HTMLInputElement | null>(null);

function isMandatory(key: string): boolean {
  return MANDATORY_STAGE_KEYS.includes(key);
}

function getNextColor(): string {
  const used = (props.stages ?? DEFAULT_COLUMNS).map((s) => s.color);
  return STAGE_COLORS.find((c) => !used.includes(c)) ?? STAGE_COLORS[0];
}

async function openAddStage() {
  showAddStage.value = true;
  await nextTick();
  addStageInputRef.value?.focus();
}

function cancelAddStage() {
  showAddStage.value = false;
  newStageName.value = '';
}

function submitAddStage() {
  const key = newStageName.value.trim();
  if (!key) return;
  emit('add-stage', { key, label: key, color: getNextColor() });
  newStageName.value = '';
  showAddStage.value = false;
}

function startEditStage(stage: StageData) {
  if (isMandatory(stage.key)) return;
  editingStageKey.value = stage.key;
  editingStageLabel.value = stage.label;
}

function commitEditStage() {
  if (!editingStageKey.value) return;
  if (isMandatory(editingStageKey.value)) {
    cancelEditStage();
    return;
  }
  const label = editingStageLabel.value.trim();
  if (!label) {
    cancelEditStage();
    return;
  }
  const stage = (props.stages ?? DEFAULT_COLUMNS).find((s) => s.key === editingStageKey.value);
  if (stage && label !== stage.label) {
    const oldKey = stage.key;
    emit('update-stage', { oldKey, stage: { ...stage, key: label, label } });
  }
  editingStageKey.value = null;
}

function cancelEditStage() {
  editingStageKey.value = null;
  editingStageLabel.value = '';
}

async function startQuickAdd(statusKey: string) {
  addingJobForStatus.value = statusKey;
  quickAddTitle.value = '';
  quickAddCompany.value = '';
  await nextTick();
  quickTitleInputRef.value?.focus();
}

function commitQuickAdd() {
  if (!quickAddTitle.value.trim() || !quickAddCompany.value.trim() || !addingJobForStatus.value)
    return;
  emit('add-job', {
    title: quickAddTitle.value.trim(),
    company_name: quickAddCompany.value.trim() || undefined,
    status: addingJobForStatus.value
  });
  addingJobForStatus.value = null;
}

function cancelQuickAdd() {
  addingJobForStatus.value = null;
}

const COLUMNS = computed(() => (props.stages?.length ? props.stages : DEFAULT_COLUMNS));

const jobsByStatus = computed(() => {
  const map: Record<string, JobData[]> = {};
  COLUMNS.value.forEach((col) => {
    map[col.key] = [];
  });
  const firstKey = COLUMNS.value[0]?.key ?? 'Saved';
  props.jobs.forEach((job) => {
    if (map[job.status] !== undefined) {
      map[job.status].push(job);
    } else {
      if (!map[firstKey]) map[firstKey] = [];
      map[firstKey].push(job);
    }
  });
  return map;
});

// ── Drag-and-drop ─────────────────────────────────────────────────────────────
let draggedJob: JobData | null = null;

function onDragStart(job: JobData) {
  draggedJob = job;
}

function onDragOver(event: DragEvent) {
  event.preventDefault()
  ;(event.currentTarget as HTMLElement).classList.add('ring-2', 'ring-primary/50');
}

function onDragLeave(event: DragEvent) {
  (event.currentTarget as HTMLElement).classList.remove('ring-2', 'ring-primary/50');
}

function onDrop(event: DragEvent, targetStatus: string) {
  event.preventDefault()
  ;(event.currentTarget as HTMLElement).classList.remove('ring-2', 'ring-primary/50');
  if (draggedJob && draggedJob.status !== targetStatus) {
    emit('status-change', draggedJob.id, targetStatus);
  }
  draggedJob = null;
}

function openUrl(url: string) {
  window.open(url, '_blank');
}

function formatDate(dateStr?: string) {
  if (!dateStr) return null;
  return new Date(dateStr).toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
}

function locationText(job: JobData): string {
  return [job.location?.city, job.location?.country].filter(Boolean).join(', ');
}
</script>

<template>
  <ScrollAreaRoot class="w-full">
    <ScrollAreaViewport class="w-full">
      <div class="flex gap-3 pb-2 pr-2 min-w-max">
        <!-- ── Columns ─────────────────────────────────────────────────────── -->
        <div v-for="col in COLUMNS" :key="col.key" class="w-64 flex flex-col gap-2 flex-shrink-0">
          <!-- Column header -->
          <div class="flex items-center justify-between px-1 group/col">
            <div class="flex items-center gap-2 min-w-0 flex-1">
              <div :class="['w-2 h-2 rounded-full flex-shrink-0', col.color]" />

              <!-- Editing mode -->
              <input
                v-if="editingStageKey === col.key"
                v-model="editingStageLabel"
                class="flex-1 text-sm font-medium bg-transparent border-b border-primary outline-none px-0.5 min-w-0"
                @keyup.enter="commitEditStage"
                @keyup.escape="cancelEditStage"
                @blur="commitEditStage"
                autofocus
              />
              <!-- Display mode -->
              <span
                v-else
                :class="[
                  'text-sm font-medium truncate select-none',
                  stages && !isMandatory(col.key)
                    ? 'cursor-pointer hover:text-primary transition-colors'
                    : ''
                ]"
                :title="
                  isMandatory(col.key)
                    ? 'Standard stage — cannot be renamed'
                    : stages
                      ? 'Click to rename'
                      : undefined
                "
                @click="stages && startEditStage(col)"
                >{{ col.label }}</span
              >
              <Icon
                v-if="isMandatory(col.key)"
                name="Lock"
                class="w-3 h-3 text-muted-foreground/60 flex-shrink-0"
              />
            </div>

            <div class="flex items-center gap-1 flex-shrink-0">
              <span class="text-xs text-muted-foreground bg-muted px-1.5 py-0.5 rounded-full">
                {{ jobsByStatus[col.key]?.length ?? 0 }}
              </span>
              <button
                v-if="stages && stages.length > 1 && !isMandatory(col.key)"
                class="opacity-0 group-hover/col:opacity-100 transition-opacity p-0.5 text-muted-foreground hover:text-destructive"
                title="Remove stage"
                @click="$emit('remove-stage', col.key)"
              >
                <svg
                  class="w-3.5 h-3.5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>

          <!-- Drop zone -->
          <div
            class="flex flex-col gap-2 min-h-[100px] rounded-lg bg-muted/40 p-2 transition-all"
            @dragover="onDragOver"
            @dragleave="onDragLeave"
            @drop="onDrop($event, col.key)"
          >
            <!-- Job cards -->
            <div
              v-for="job in jobsByStatus[col.key]"
              :key="job.id"
              draggable="true"
              @dragstart="onDragStart(job)"
              @click="$emit('edit', job)"
              class="relative bg-card border border-border rounded-md p-3 cursor-pointer hover:shadow-md hover:border-primary/30 transition-all group"
            >
              <!-- Three-dots menu: absolute top-right -->
              <DropdownMenu>
                <DropdownMenuTrigger as-child>
                  <Button
                    variant="ghost"
                    size="icon"
                    class="absolute top-1 right-1 h-6 w-6 opacity-0 group-hover:opacity-100 transition-opacity z-10"
                    @click.stop
                  >
                    <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <circle cx="10" cy="4" r="1.5" />
                      <circle cx="10" cy="10" r="1.5" />
                      <circle cx="10" cy="16" r="1.5" />
                    </svg>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" @click.stop>
                  <DropdownMenuItem @click.stop="$emit('edit', job)">Edit</DropdownMenuItem>
                  <template v-if="job.source_url">
                    <DropdownMenuSeparator />
                    <DropdownMenuItem @click.stop="openUrl(job.source_url!)"
                      >Open Job URL</DropdownMenuItem
                    >
                  </template>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem
                    class="text-destructive focus:text-destructive"
                    @click.stop="$emit('delete', job.id)"
                    >Delete</DropdownMenuItem
                  >
                </DropdownMenuContent>
              </DropdownMenu>

              <p class="text-sm font-medium leading-tight line-clamp-2 mb-1.5 pr-5">
                {{ job.title }}
              </p>
              <div v-if="job.company" class="flex items-center gap-1.5 mb-1.5 min-w-0">
                <img
                  :src="job.company.logo_url || DEFAULT_COMPANY_LOGO_URL"
                  class="w-5 h-5 rounded-full object-contain flex-shrink-0 bg-muted"
                  @error="($event.target as HTMLImageElement).style.display = 'none'"
                />
                <p class="text-xs text-muted-foreground truncate">{{ job.company.name }}</p>
              </div>

              <div v-if="locationText(job)" class="flex items-center gap-1 mb-2 min-w-0">
                <MapPin class="w-3 h-3 text-muted-foreground/70 flex-shrink-0" />
                <p class="text-xs text-muted-foreground truncate">{{ locationText(job) }}</p>
              </div>

              <div class="flex flex-wrap gap-1 mb-2">
                <Badge v-if="job.work_model" variant="outline" class="text-xs px-1.5 py-0">{{
                  job.work_model
                }}</Badge>
                <Badge v-if="job.source_platform" variant="outline" class="text-xs px-1.5 py-0">{{
                  job.source_platform
                }}</Badge>
              </div>

              <div class="flex items-center mt-1">
                <span v-if="job.applied_date" class="text-xs text-muted-foreground">{{
                  formatDate(job.applied_date)
                }}</span>
                <span v-else-if="job.created_at" class="text-xs text-muted-foreground">{{
                  formatDate(job.created_at)
                }}</span>
              </div>
            </div>

            <!-- Empty column placeholder -->
            <div
              v-if="jobsByStatus[col.key]?.length === 0"
              class="flex items-center justify-center h-12 text-xs text-muted-foreground/50 border-2 border-dashed border-muted-foreground/20 rounded-md"
            ></div>
          </div>

          <!-- Quick-add card area -->
          <div>
            <!-- Trigger -->
            <button
              v-if="addingJobForStatus !== col.key"
              class="w-full flex items-center gap-1.5 px-2 py-1.5 rounded-md text-xs text-muted-foreground hover:text-foreground hover:bg-muted/60 transition-colors"
              @click="startQuickAdd(col.key)"
            >
              <svg
                class="w-3.5 h-3.5 flex-shrink-0"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                stroke-width="2"
              >
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4" />
              </svg>
              Add a card
            </button>

            <!-- Inline form -->
            <div
              v-else
              class="flex flex-col gap-1.5 p-2 bg-card rounded-md border border-primary/30 shadow-sm"
            >
              <input
                :ref="
                  (el) => {
                    if (addingJobForStatus === col.key) quickTitleInputRef = el as HTMLInputElement
                  }
                "
                v-model="quickAddTitle"
                class="w-full rounded border border-input bg-background px-2 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-ring"
                placeholder="Job title..."
                @keyup.escape="cancelQuickAdd"
              />
              <input
                v-model="quickAddCompany"
                class="w-full rounded border border-input bg-background px-2 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-ring"
                placeholder="Company *"
                @keyup.enter="commitQuickAdd"
                @keyup.escape="cancelQuickAdd"
              />
              <div class="flex gap-1.5">
                <button
                  class="flex-1 text-xs py-1.5 rounded bg-primary text-primary-foreground font-medium disabled:opacity-50 transition-colors"
                  :disabled="!quickAddTitle.trim() || !quickAddCompany.trim()"
                  @click="commitQuickAdd"
                >
                  Add card
                </button>
                <button
                  class="flex-1 text-xs py-1.5 rounded border border-border text-muted-foreground hover:text-foreground transition-colors"
                  @click="cancelQuickAdd"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- ── Add List column (only when board has custom stages) ──────────── -->
        <div v-if="stages" class="w-60 flex-shrink-0 flex flex-col gap-2">
          <!-- Spacer aligns with column headers -->
          <div class="h-6" />

          <!-- Collapsed: "+ Add a list" button -->
          <div v-if="!showAddStage">
            <button
              class="w-full flex items-center gap-2 px-3 py-2.5 rounded-lg border-2 border-dashed border-muted-foreground/20 text-sm text-muted-foreground hover:border-primary/40 hover:text-primary hover:bg-muted/10 transition-colors"
              @click="openAddStage"
            >
              <svg
                class="w-4 h-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                stroke-width="2"
              >
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4" />
              </svg>
              Add a list
            </button>
          </div>

          <!-- Expanded: input form -->
          <div
            v-else
            class="flex flex-col gap-2 p-3 rounded-lg border border-border bg-card shadow-sm"
          >
            <div class="flex items-center gap-2">
              <div :class="['w-3 h-3 rounded-full flex-shrink-0', getNextColor()]" />
            </div>
            <input
              ref="addStageInputRef"
              v-model="newStageName"
              class="w-full rounded-md border border-input bg-background px-2 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-ring"
              placeholder="List name..."
              @keyup.enter="submitAddStage"
              @keyup.escape="cancelAddStage"
            />
            <div class="flex gap-1.5">
              <button
                class="flex-1 text-xs py-1.5 rounded-md bg-primary text-primary-foreground font-medium disabled:opacity-50"
                :disabled="!newStageName.trim()"
                @click="submitAddStage"
              >
                Add list
              </button>
              <button
                class="flex-1 text-xs py-1.5 rounded-md border border-border text-muted-foreground hover:text-foreground"
                @click="cancelAddStage"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      </div>
    </ScrollAreaViewport>

    <!-- Horizontal scrollbar (shadcn style) -->
    <ScrollAreaScrollbar
      orientation="horizontal"
      class="flex h-2.5 touch-none select-none flex-col border-t border-t-transparent p-px transition-colors"
    >
      <ScrollAreaThumb class="relative flex-1 rounded-full bg-border" />
    </ScrollAreaScrollbar>
    <ScrollAreaCorner />
  </ScrollAreaRoot>
</template>
