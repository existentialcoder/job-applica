<script setup lang="ts">
import { h } from 'vue';
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
}>();

const emit = defineEmits<{
  (e: 'selection-change', jobs: JobData[]): void
  (e: 'edit', job: JobData): void
  (e: 'status-change', jobId: number, status: string): void
}>();

function handleRowClick(row: RowData) {
  emit('edit', row._raw);
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

const STATUS_NEXT: Record<string, string[]> = {
  Saved: ['Applied', 'Rejected', 'Withdrawn'],
  Applied: ['Phone Screen', 'Interview', 'Rejected', 'Withdrawn'],
  'Phone Screen': ['Interview', 'Technical', 'Rejected', 'Withdrawn'],
  Interview: ['Technical', 'Offer', 'Rejected', 'Withdrawn'],
  Technical: ['Offer', 'Rejected', 'Withdrawn'],
  Offer: ['Withdrawn'],
  Rejected: ['Saved'],
  Withdrawn: ['Saved'],
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
          h(DropdownMenuSeparator),
          ...(STATUS_NEXT[row.original.status] || []).map(s =>
            h(DropdownMenuItem, {
              onClick: () => emit('status-change', row.original.id, s),
            }, () => `Mark as ${s}`)
          ),
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
  <div>
    <DataTable :columns="columns" :data="transformRows(jobs)" :on-row-click="handleRowClick" />
  </div>
</template>
