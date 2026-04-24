<script setup lang="ts">
import { computed } from 'vue';
import type { JobData } from '@/lib/types';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

const props = defineProps<{
  jobs: JobData[]
}>();

const emit = defineEmits<{
  (e: 'edit', job: JobData): void
  (e: 'status-change', jobId: number, status: string): void
}>();

const COLUMNS = [
  { key: 'Saved', label: 'Saved', color: 'bg-slate-500' },
  { key: 'Applied', label: 'Applied', color: 'bg-blue-500' },
  { key: 'Phone Screen', label: 'Phone Screen', color: 'bg-amber-500' },
  { key: 'Interview', label: 'Interview', color: 'bg-amber-500' },
  { key: 'Technical', label: 'Technical', color: 'bg-orange-500' },
  { key: 'Offer', label: 'Offer', color: 'bg-emerald-500' },
  { key: 'Rejected', label: 'Rejected', color: 'bg-red-500' },
  { key: 'Withdrawn', label: 'Withdrawn', color: 'bg-zinc-400' },
];

const statusVariants: Record<string, string> = {
  Saved: 'secondary',
  Applied: 'default',
  'Phone Screen': 'warning',
  Interview: 'warning',
  Technical: 'warning',
  Offer: 'success',
  Rejected: 'danger',
  Withdrawn: 'outline',
};

const jobsByStatus = computed(() => {
  const map: Record<string, JobData[]> = {};
  COLUMNS.forEach(col => { map[col.key] = []; });
  props.jobs.forEach(job => {
    if (map[job.status]) {
      map[job.status].push(job);
    } else {
      map['Saved'] = map['Saved'] || [];
      map['Saved'].push(job);
    }
  });
  return map;
});

// ── Drag-and-drop state ───────────────────────────────────────────────────────
let draggedJob: JobData | null = null;

function onDragStart(job: JobData) {
  draggedJob = job;
}

function onDragOver(event: DragEvent) {
  event.preventDefault();
  (event.currentTarget as HTMLElement).classList.add('ring-2', 'ring-primary/50');
}

function onDragLeave(event: DragEvent) {
  (event.currentTarget as HTMLElement).classList.remove('ring-2', 'ring-primary/50');
}

function onDrop(event: DragEvent, targetStatus: string) {
  event.preventDefault();
  (event.currentTarget as HTMLElement).classList.remove('ring-2', 'ring-primary/50');
  if (draggedJob && draggedJob.status !== targetStatus) {
    emit('status-change', draggedJob.id, targetStatus);
  }
  draggedJob = null;
}

function formatDate(dateStr?: string) {
  if (!dateStr) return null;
  return new Date(dateStr).toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
}
</script>

<template>
  <div class="overflow-x-auto pb-4">
    <div class="flex gap-3 min-w-max">
      <div
        v-for="col in COLUMNS"
        :key="col.key"
        class="w-64 flex flex-col gap-2 flex-shrink-0"
      >
        <!-- Column header -->
        <div class="flex items-center justify-between px-1">
          <div class="flex items-center gap-2">
            <div :class="['w-2 h-2 rounded-full', col.color]" />
            <span class="text-sm font-medium">{{ col.label }}</span>
          </div>
          <span class="text-xs text-muted-foreground bg-muted px-1.5 py-0.5 rounded-full">
            {{ jobsByStatus[col.key]?.length ?? 0 }}
          </span>
        </div>

        <!-- Drop zone -->
        <div
          class="flex flex-col gap-2 min-h-[120px] rounded-lg bg-muted/40 p-2 transition-all"
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
            class="bg-card border border-border rounded-md p-3 cursor-pointer hover:shadow-md hover:border-primary/30 transition-all group"
          >
            <!-- Title -->
            <p class="text-sm font-medium leading-tight line-clamp-2 mb-1.5">{{ job.title }}</p>

            <!-- Company -->
            <p v-if="job.company" class="text-xs text-muted-foreground truncate mb-2">
              {{ job.company.name }}
            </p>

            <!-- Tags row -->
            <div class="flex flex-wrap gap-1 mb-2">
              <Badge v-if="job.work_model" variant="outline" class="text-xs px-1.5 py-0">
                {{ job.work_model }}
              </Badge>
              <Badge v-if="job.source_platform" variant="outline" class="text-xs px-1.5 py-0">
                {{ job.source_platform }}
              </Badge>
            </div>

            <!-- Footer: date + actions -->
            <div class="flex items-center justify-between mt-1">
              <span v-if="job.applied_date" class="text-xs text-muted-foreground">
                {{ formatDate(job.applied_date) }}
              </span>
              <span v-else-if="job.created_at" class="text-xs text-muted-foreground">
                {{ formatDate(job.created_at) }}
              </span>
              <Button
                variant="ghost"
                size="icon"
                class="h-6 w-6 opacity-0 group-hover:opacity-100 transition-opacity"
                @click.stop="$emit('edit', job)"
              >
                <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
              </Button>
            </div>
          </div>

          <!-- Empty column placeholder -->
          <div v-if="jobsByStatus[col.key]?.length === 0"
            class="flex items-center justify-center h-16 text-xs text-muted-foreground/50 border-2 border-dashed border-muted-foreground/20 rounded-md">
            Drop here
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
