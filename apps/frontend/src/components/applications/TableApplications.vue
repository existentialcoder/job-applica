<script setup lang="ts">
import { DataTable, type ColumnDef } from '@/components/ui/data-table';
import { ref, h } from 'vue';
import type { JobData } from '@/lib/types';
import { Checkbox } from '@/components/ui/checkbox';
import DataTableHeader from '@/components/ui/data-table/DataTableHeader.vue';
import type { Column } from '@tanstack/vue-table';
import { Badge } from '@/components/ui/badge';

const props = defineProps<{
  jobs: JobData[]
}>();

const emit = defineEmits<{
  (e: 'selection-change', selectedJobs: any): void
}>();

interface IData {
  id: string

  title: string
  company: string
  status: string
}

const statusVariants: Record<string, string> = {
  applied: 'info',        // Blue — represents action taken
  saved: 'secondary',     // Gray — neutral, passive state
  rejected: 'danger',     // Red — error or negative outcome
  interviewed: 'warning', // Yellow/Amber — pending or in-progress stage
};

const columns: ColumnDef<IData>[] = [
  {
    accessorKey: 'id',
    header: ({ table }) => h(Checkbox, {
      checked: table.getIsAllPageRowsSelected(),
      'onUpdate:checked': val => {
        table.toggleAllPageRowsSelected(!!val);
        emit('selection-change', table.getSelectedRowModel().flatRows.map(row => row.original));
      },
      ariaLabel: 'Select All',
      class: 'translate-y-0.5',
    }),
    cell: ({ table, row }) => h(Checkbox, {
      checked: row.getIsSelected(),
      'onUpdate:checked': val => {
        row.toggleSelected(!!val);
        emit('selection-change', table.getSelectedRowModel().flatRows.map(row => row.original));
      },
      'ariaLabel': 'Select row',
      class: 'translate-y-0.5',
      enableSorting: false,
      enableHiding: false,
    })
  },
  {
    accessorKey: 'id',
    header: 'ID',
    enableSorting: false,
  },
  {
    accessorKey: 'title',
    header: ({ column }) => h(DataTableHeader, {
      column: column as Column<IData>,
      title: 'Job Title',
      'onUpdate:sort': (val) => {
        console.log(val)
      },
    })
  },
  {
    accessorKey: 'company',
    header: 'Company',
    enableSorting: false,
  },
  {
    accessorKey: 'status',
    header: 'Status',
    cell: ({ row }) => h('div', {
      class: 'max-w-[500px] truncate flex items-center',
    }, [
      h(Badge, {
        variant: (statusVariants[row.original.status] as any),
        class: 'mr-2',
      }, () => row.original.status),
    ]),
    enableSorting: false,
  },
  {
    id: 'actions',
  },
];

function transformAsList(jobs: JobData[]) {
  return jobs.map(job => ({
    id: job.job_id,
    title: job.job_title.split(':')[1].trim(),
    company: job.company,
    status: job.status
  }));
}

</script>

<template>
  <div>
    <DataTable :columns="columns" :data="transformAsList(jobs)"></DataTable>
  </div>
</template>