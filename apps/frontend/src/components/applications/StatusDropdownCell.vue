<script setup lang="ts">
import { Check } from 'lucide-vue-next';
import { Badge } from '@/components/ui/badge';
import {
  DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { cn } from '@/lib/utils';

const props = defineProps<{
  jobId: number
  status: string
  statusOptions: string[]
}>();

const emit = defineEmits<{
  (e: 'change', jobId: number, status: string): void
}>();

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
</script>

<template>
  <DropdownMenu>
    <DropdownMenuTrigger class="cursor-pointer outline-none">
      <Badge :variant="(statusVariants[status] as any) || 'outline'">{{ status }}</Badge>
    </DropdownMenuTrigger>
    <DropdownMenuContent align="start">
      <DropdownMenuItem
        v-for="s in statusOptions"
        :key="s"
        :class="cn('gap-2 cursor-pointer', s === status && 'font-medium')"
        @click="emit('change', jobId, s)"
      >
        <Check :class="cn('h-4 w-4 shrink-0', s !== status && 'invisible')" />
        {{ s }}
      </DropdownMenuItem>
    </DropdownMenuContent>
  </DropdownMenu>
</template>
