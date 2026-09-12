<script setup lang="ts">
import { Check } from 'lucide-vue-next';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger
} from '@/components/ui/dropdown-menu';
import { cn } from '@/lib/utils';
import StageBadge from './StageBadge.vue';

const emit = defineEmits<{
  (e: 'change', jobId: number, status: string): void;
}>();

defineProps<{
  jobId: number;
  status: string;
  statusOptions: string[];
  color?: string;
}>();
</script>

<template>
  <DropdownMenu>
    <DropdownMenuTrigger class="cursor-pointer outline-none">
      <StageBadge :color="color" :label="status" />
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
