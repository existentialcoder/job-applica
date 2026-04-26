<script setup lang="ts">
import { h, ref, nextTick } from 'vue';
import type { JobData } from '@/lib/types';
import { DataTable, type ColumnDef } from '@/components/ui/data-table';
import { Checkbox } from '@/components/ui/checkbox';
import DataTableHeader from '@/components/ui/data-table/DataTableHeader.vue';
import type { Column } from '@tanstack/vue-table';
import { Badge } from '@/components/ui/badge';
import {
  DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator, DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Button } from '@/components/ui/button';

const props = defineProps<{
  jobs: JobData[]
  statusOptions?: string[]
}>();

const emit = defineEmits<{
  (e: 'selection-change', jobs: JobData[]): void
  (e: 'edit', job: JobData): void
  (e: 'status-change', jobId: number, status: string): void
  (e: 'add-quick', payload: { title: string; company_name?: string; status: string }): void
}>();

// ── Inline new-row state ──────────────────────────────────────────────────────
const showAddRow = ref(false);
const addTitle = ref('');
const addCompany = ref('');
const addStatus = ref('');
const addTitleRef = ref<HTMLInputElement | null>(null);

async function openAddRow() {
  addTitle.value = '';
  addCompany.value = '';
  addStatus.value = props.statusOptions?.[0] ?? 'Saved';
  showAddRow.value = true;
  await nextTick();
  addTitleRef.value?.focus();
}

function submitAdd() {
  if (!addTitle.value.trim()) return;
  emit('add-quick', {
    title: addTitle.value.trim(),
    company_name: addCompany.value.trim() || undefined,
    status: addStatus.value || props.statusOptions?.[0] || 'Saved',
  });
  showAddRow.value = false;
}

function cancelAdd() {
  showAddRow.value = false;
}

// Mapped from JobData for the table
interface RowData {
  _raw: JobData
  id: number
  title: string
  company: string
  location: string
  status: string
  platform: string
  work_model: string
}

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


const columns: ColumnDef<RowData>[] = [
  {
    id: 'select',
    header: ({ table }) => h(Checkbox, {
      checked: table.getIsAllPageRowsSelected(),
      'onUpdate:checked': (val: boolean) => {
        table.toggleAllPageRowsSelected(!!val);
        emit('selection-change', table.getSelectedRowModel().flatRows.map(r => r.original._raw));
      },
      ariaLabel: 'Select All',
      class: 'translate-y-0.5',
    }),
    cell: ({ table, row }) => h(Checkbox, {
      checked: row.getIsSelected(),
      'onUpdate:checked': (val: boolean) => {
        row.toggleSelected(!!val);
        emit('selection-change', table.getSelectedRowModel().flatRows.map(r => r.original._raw));
      },
      ariaLabel: 'Select row',
      class: 'translate-y-0.5',
    }),
    enableSorting: false,
  },
  {
    accessorKey: 'title',
    header: ({ column }) => h(DataTableHeader, {
      column: column as Column<RowData>,
      title: 'Job Title',
    }),
    cell: ({ row }) => h('div', { class: 'flex flex-col' }, [
      h('span', { class: 'font-medium truncate max-w-[200px]' }, row.original.title),
      row.original.platform
        ? h('span', { class: 'text-xs text-muted-foreground' }, row.original.platform)
        : null,
    ]),
  },
  {
    accessorKey: 'company',
    header: 'Company',
    cell: ({ row }) => h('span', { class: 'truncate max-w-[150px] block' }, row.original.company || '—'),
    enableSorting: false,
  },
  {
    accessorKey: 'location',
    header: 'Location',
    cell: ({ row }) => h('span', { class: 'text-sm truncate max-w-[140px] block' }, row.original.location || '—'),
    enableSorting: false,
  },
  {
    accessorKey: 'work_model',
    header: 'Work Type',
    cell: ({ row }) => row.original.work_model
      ? h(Badge, { variant: 'outline', class: 'text-xs' }, () => row.original.work_model)
      : h('span', { class: 'text-muted-foreground text-sm' }, '—'),
    enableSorting: false,
  },
  {
    accessorKey: 'status',
    header: 'Status',
    cell: ({ row }) => h(Badge, {
      variant: (statusVariants[row.original.status] as any) || 'outline',
    }, () => row.original.status),
    enableSorting: false,
  },
  {
    id: 'actions',
    cell: ({ row }) => h(DropdownMenu, {}, {
      default: () => [
        h(DropdownMenuTrigger, { asChild: true }, () =>
          h(Button, { variant: 'ghost', size: 'icon', class: 'h-8 w-8' }, () =>
            h('svg', { class: 'w-4 h-4', fill: 'currentColor', viewBox: '0 0 20 20' }, [
              h('circle', { cx: '10', cy: '4', r: '1.5' }),
              h('circle', { cx: '10', cy: '10', r: '1.5' }),
              h('circle', { cx: '10', cy: '16', r: '1.5' }),
            ])
          )
        ),
        h(DropdownMenuContent, { align: 'end' }, () => [
          h(DropdownMenuItem, { onClick: () => emit('edit', row.original._raw) }, () => 'Edit'),
          row.original._raw.source_url
            ? h(DropdownMenuSeparator)
            : null,
          row.original._raw.source_url
            ? h(DropdownMenuItem, {
              onClick: () => window.open(row.original._raw.source_url, '_blank'),
            }, () => 'Open Job URL')
            : null,
        ]),
      ],
    }),
  },
];

function transformRows(jobs: JobData[]): RowData[] {
  return jobs.map(job => ({
    _raw: job,
    id: job.id,
    title: job.title,
    company: job.company?.name || '',
    location: [job.location?.city, job.location?.state].filter(Boolean).join(', '),
    status: job.status,
    platform: job.source_platform || '',
    work_model: job.work_model || '',
  }));
}
</script>

<template>
  <div class="flex flex-col">
    <DataTable :columns="columns" :data="transformRows(jobs)" />

    <!-- Inline new-row (Airtable/Notion style) -->
    <div class="border border-t-0 border-border rounded-b-md overflow-hidden">
      <!-- Collapsed trigger -->
      <button
        v-if="!showAddRow"
        class="w-full flex items-center gap-2 px-4 py-2 text-sm text-muted-foreground hover:bg-muted/30 hover:text-foreground transition-colors"
        @click="openAddRow"
      >
        <svg class="w-3.5 h-3.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4" />
        </svg>
        New Application
      </button>

      <!-- Expanded inline form -->
      <div v-else class="flex items-center gap-2 px-3 py-2 bg-muted/10 border-t border-border/50">
        <input
          ref="addTitleRef"
          v-model="addTitle"
          class="flex-1 min-w-0 rounded border border-input bg-background px-2 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-ring"
          placeholder="Job title *"
          @keyup.enter="submitAdd"
          @keyup.escape="cancelAdd"
        />
        <input
          v-model="addCompany"
          class="w-36 rounded border border-input bg-background px-2 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-ring"
          placeholder="Company"
          @keyup.enter="submitAdd"
          @keyup.escape="cancelAdd"
        />
        <select
          v-model="addStatus"
          class="w-36 rounded border border-input bg-background px-2 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-ring"
        >
          <option v-for="s in (statusOptions ?? ['Saved'])" :key="s" :value="s">{{ s }}</option>
        </select>
        <button
          class="px-3 py-1.5 text-xs rounded bg-primary text-primary-foreground font-medium disabled:opacity-50 transition-colors"
          :disabled="!addTitle.trim()"
          @click="submitAdd"
        >Add</button>
        <button
          class="px-3 py-1.5 text-xs rounded border border-border text-muted-foreground hover:text-foreground transition-colors"
          @click="cancelAdd"
        >Cancel</button>
      </div>
    </div>
  </div>
</template>
