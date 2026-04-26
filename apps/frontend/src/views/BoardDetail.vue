<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import type { BoardData, JobData, JobCreatePayload } from '@/lib/types';
import dataservice from '@/lib/dataservice';
import { Button } from '@/components/ui/button';
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter,
} from '@/components/ui/dialog';
import {
  DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator, DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import Applications from '@/views/Applications.vue';
import { BoardSettingsModal } from '@/components/applications';
import { useAppStore } from '@/stores/app';

const route = useRoute();
const router = useRouter();
const appStore = useAppStore();

const boardId = computed(() => Number(route.params.boardId));
const board = ref<BoardData | null>(null);
const isLoading = ref(true);
const isNotFound = ref(false);

const isSettingsOpen = ref(false);
const isSaving = ref(false);

const isDeleteOpen = ref(false);
const isDeleting = ref(false);

const isImporting = ref(false);
const importInputRef = ref<HTMLInputElement | null>(null);
const refreshCounter = ref(0);

async function loadBoard() {
  isLoading.value = true;
  const data = await dataservice.getBoard(boardId.value);
  if (!data) {
    isNotFound.value = true;
    isLoading.value = false;
    return;
  }

  // Auto-heal stages where key ≠ label (artifact of the old rename bug).
  // Silently migrate jobs and fix the stored keys so the UI and DB stay in sync.
  const mismatched = data.stages.filter(s => s.key !== s.label);
  if (mismatched.length > 0) {
    const keyRenames: Record<string, string> = {};
    const fixedStages = data.stages.map(s => {
      if (s.key !== s.label) { keyRenames[s.key] = s.label; return { ...s, key: s.label }; }
      return s;
    });
    const fixed = await dataservice.updateBoard(data.id, { stages: fixedStages, key_renames: keyRenames });
    board.value = fixed ?? data;
  } else {
    board.value = data;
  }

  appStore.setBreadcrumbs([
    { label: 'Boards', path: '/boards' },
    { label: board.value!.name },
  ]);
  isLoading.value = false;
}

async function saveSettings(payload: { name: string; description: string; color: string; stages: { key: string; label: string; color: string }[]; key_renames: Record<string, string> }) {
  if (!board.value) return;
  isSaving.value = true;
  const updated = await dataservice.updateBoard(board.value.id, {
    name: payload.name,
    color: payload.color,
    description: payload.description || undefined,
    stages: payload.stages,
    key_renames: Object.keys(payload.key_renames).length > 0 ? payload.key_renames : undefined,
  });
  isSaving.value = false;
  if (updated) {
    board.value = updated;
    appStore.setBreadcrumbs([
      { label: 'Boards', path: '/boards' },
      { label: updated.name },
    ]);
    isSettingsOpen.value = false;
    if (Object.keys(payload.key_renames).length > 0) refreshCounter.value++;
  }
}

async function confirmDelete() {
  if (!board.value) return;
  isDeleting.value = true;
  const ok = await dataservice.deleteBoard(board.value.id);
  isDeleting.value = false;
  if (ok) router.push('/boards');
}

// ── Download ──────────────────────────────────────────────────────────────────
function triggerDownload(content: string, filename: string, type: string) {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

function toCSV(jobs: JobData[]): string {
  const headers = ['title', 'company', 'location', 'status', 'work_model', 'salary_range', 'platform', 'source_url', 'applied_date', 'notes'];
  const rows = jobs.map(job => [
    job.title,
    job.company?.name ?? '',
    job.location ? [job.location.city, job.location.state, job.location.country].filter(Boolean).join(', ') : '',
    job.status,
    job.work_model ?? '',
    job.salary_range ?? '',
    job.source_platform ?? '',
    job.source_url ?? '',
    job.applied_date ?? '',
    job.notes ?? '',
  ].map(v => `"${String(v ?? '').replace(/"/g, '""')}"`).join(','));
  return [headers.join(','), ...rows].join('\r\n');
}

async function getAllBoardJobs() {
  if (!board.value) return [];
  const PAGE = 100;
  const first = await dataservice.getJobs({ board_id: board.value.id, page: 1, per_page: PAGE });
  const all = [...first.items];
  const pages = Math.ceil(first.total / PAGE);
  for (let p = 2; p <= pages; p++) {
    const res = await dataservice.getJobs({ board_id: board.value.id, page: p, per_page: PAGE });
    all.push(...res.items);
  }
  return all;
}

async function downloadAs(format: 'json' | 'csv') {
  if (!board.value) return;
  const jobs = await getAllBoardJobs();
  const name = board.value.name.replace(/[^a-z0-9]/gi, '-').toLowerCase();
  if (format === 'json') {
    triggerDownload(JSON.stringify(jobs, null, 2), `${name}-jobs.json`, 'application/json');
  } else {
    triggerDownload(toCSV(jobs), `${name}-jobs.csv`, 'text/csv;charset=utf-8;');
  }
}

// ── Import ────────────────────────────────────────────────────────────────────
function triggerImport() {
  importInputRef.value?.click();
}

function parseCSVLine(line: string): string[] {
  const result: string[] = [];
  let current = '';
  let inQuotes = false;
  for (let i = 0; i < line.length; i++) {
    if (line[i] === '"') {
      if (inQuotes && line[i + 1] === '"') { current += '"'; i++; }
      else inQuotes = !inQuotes;
    } else if (line[i] === ',' && !inQuotes) {
      result.push(current); current = '';
    } else {
      current += line[i];
    }
  }
  result.push(current);
  return result;
}

async function handleImport(event: Event) {
  const file = (event.target as HTMLInputElement).files?.[0];
  if (!file || !board.value) return;
  isImporting.value = true;
  try {
    const text = await file.text();
    const ext = file.name.split('.').pop()?.toLowerCase();
    let payloads: JobCreatePayload[] = [];

    if (ext === 'json') {
      const data = JSON.parse(text);
      const items: any[] = Array.isArray(data) ? data : [data];
      payloads = items.filter(item => item.title).map(item => ({
        title: item.title,
        company_name: item.company?.name ?? item.company_name,
        location: item.location
          ? (typeof item.location === 'string'
            ? item.location
            : [item.location.city, item.location.state].filter(Boolean).join(', '))
          : undefined,
        status: item.status ?? board.value!.stages[0]?.key,
        work_model: item.work_model,
        salary_range: item.salary_range,
        source_platform: item.source_platform,
        source_url: item.source_url,
        applied_date: item.applied_date,
        notes: item.notes,
        board_id: board.value!.id,
      }));
    } else if (ext === 'csv') {
      const lines = text.split(/\r?\n/).filter(l => l.trim());
      if (lines.length < 2) return;
      const headers = parseCSVLine(lines[0]);
      payloads = lines.slice(1).map(line => {
        const values = parseCSVLine(line);
        const row: Record<string, string> = {};
        headers.forEach((h, i) => { row[h.trim()] = values[i] ?? ''; });
        if (!row.title) return null;
        return {
          title: row.title,
          company_name: row.company || undefined,
          location: row.location || undefined,
          status: row.status || board.value!.stages[0]?.key,
          work_model: row.work_model || undefined,
          salary_range: row.salary_range || undefined,
          source_platform: row.platform || undefined,
          source_url: row.source_url || undefined,
          applied_date: row.applied_date || undefined,
          notes: row.notes || undefined,
          board_id: board.value!.id,
        } as JobCreatePayload;
      }).filter((p): p is JobCreatePayload => p !== null);
    }

    if (payloads.length > 0) {
      await Promise.all(payloads.map(p => dataservice.createJob(p)));
      refreshCounter.value++;
    }
  } catch (e) {
    console.error('Import failed', e);
  } finally {
    isImporting.value = false;
    if (importInputRef.value) importInputRef.value.value = '';
  }
}

onMounted(loadBoard);

onUnmounted(() => {
  appStore.setBreadcrumbs([]);
});
</script>

<template>
  <div class="flex flex-col gap-4">
    <!-- Loading -->
    <div v-if="isLoading" class="flex justify-center py-16">
      <svg class="w-6 h-6 animate-spin text-muted-foreground" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
      </svg>
    </div>

    <!-- Not found -->
    <div v-else-if="isNotFound" class="flex flex-col items-center py-20 gap-3 text-center">
      <p class="font-medium">Board not found</p>
      <Button variant="outline" @click="router.push('/boards')">Back to Boards</Button>
    </div>

    <!-- Board content -->
    <template v-else-if="board">
      <!-- Board header -->
      <div class="flex items-center justify-between gap-3">
        <div class="flex items-center gap-3 min-w-0">
          <div :class="['w-3 h-3 rounded-full flex-shrink-0', board.color || 'bg-blue-500']" />
          <div class="min-w-0">
            <h1 class="text-xl font-semibold truncate">{{ board.name }}</h1>
            <p v-if="board.description" class="text-xs text-muted-foreground truncate">{{ board.description }}</p>
          </div>
        </div>

        <!-- Icon action buttons -->
        <div class="flex items-center gap-0.5 flex-shrink-0">
          <!-- Download dropdown -->
          <DropdownMenu>
            <DropdownMenuTrigger as-child>
              <Button variant="ghost" size="icon" title="Download jobs">
                <Icon name="Download" class="w-4 h-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem @click="downloadAs('json')">Download as JSON</DropdownMenuItem>
              <DropdownMenuItem @click="downloadAs('csv')">Download as CSV</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>

          <!-- Import -->
          <Button variant="ghost" size="icon" title="Import jobs (JSON or CSV)" :disabled="isImporting" @click="triggerImport">
            <Icon name="Upload" class="w-4 h-4" />
          </Button>
          <input
            ref="importInputRef"
            type="file"
            accept=".json,.csv"
            class="hidden"
            @change="handleImport"
          />

          <!-- Board actions: Settings + Delete -->
          <DropdownMenu>
            <DropdownMenuTrigger as-child>
              <Button variant="ghost" size="icon" title="Board actions">
                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <circle cx="10" cy="4" r="1.5"/>
                  <circle cx="10" cy="10" r="1.5"/>
                  <circle cx="10" cy="16" r="1.5"/>
                </svg>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem @click="isSettingsOpen = true">
                <Icon name="Settings" class="w-4 h-4 mr-2" /> Board Settings
              </DropdownMenuItem>
              <template v-if="!board.is_default">
                <DropdownMenuSeparator />
                <DropdownMenuItem
                  class="text-destructive focus:text-destructive"
                  @click="isDeleteOpen = true"
                >
                  <Icon name="Trash" class="w-4 h-4 mr-2" /> Delete Board
                </DropdownMenuItem>
              </template>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>

      <!-- Applications scoped to this board -->
      <Applications
        :key="`${board.id}-${refreshCounter}`"
        :board-id="board.id"
        :stages="board.stages"
        :default-status="board.stages[0]?.key"
        @stages-updated="(s) => { if (board) board.stages = s }"
      />
    </template>

    <!-- Board settings modal -->
    <BoardSettingsModal
      v-if="board"
      v-model:open="isSettingsOpen"
      :board="board"
      @save="saveSettings"
    />

    <!-- Delete confirm dialog -->
    <Dialog v-model:open="isDeleteOpen">
      <DialogContent class="max-w-sm">
        <DialogHeader>
          <DialogTitle>Delete Board</DialogTitle>
        </DialogHeader>
        <div class="py-2">
          <p class="text-sm text-muted-foreground">
            Are you sure you want to delete
            <strong class="text-foreground">{{ board?.name }}</strong>?
            All jobs in this board will be permanently deleted. This action cannot be undone.
          </p>
        </div>
        <DialogFooter>
          <Button variant="outline" @click="isDeleteOpen = false" :disabled="isDeleting">Cancel</Button>
          <Button variant="destructive" @click="confirmDelete" :disabled="isDeleting">
            {{ isDeleting ? 'Deleting...' : 'Delete Board' }}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  </div>
</template>
