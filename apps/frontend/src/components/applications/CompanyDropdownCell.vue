<script setup lang="ts">
import {
  DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { DEFAULT_COMPANY_LOGO_URL } from '@/lib/constants';
import type { CompanyOption } from '@/stores/companies';

const props = defineProps<{
  jobId: number
  company: string
  companyLogo?: string
  companies: CompanyOption[]
}>();

const emit = defineEmits<{
  (e: 'change', jobId: number, companyName: string): void
}>();
</script>

<template>
  <DropdownMenu>
    <DropdownMenuTrigger class="bg-transparent p-0 border-0 outline-none cursor-pointer text-left">
      <div v-if="company" class="flex items-center gap-1.5 max-w-[150px]">
        <img
          :src="companyLogo || DEFAULT_COMPANY_LOGO_URL"
          class="w-5 h-5 rounded-full object-contain flex-shrink-0 bg-muted"
          @error="($event.target as HTMLImageElement).style.display = 'none'"
        />
        <span class="truncate text-sm">{{ company }}</span>
      </div>
      <span v-else class="text-muted-foreground text-sm hover:text-foreground">+ Add company</span>
    </DropdownMenuTrigger>
    <DropdownMenuContent align="start">
      <DropdownMenuItem
        v-for="c in companies"
        :key="c.id"
        :class="c.name === company ? 'font-medium' : ''"
        class="flex items-center gap-2"
        @click="emit('change', jobId, c.name)"
      >
        <img
          :src="c.logo_url || DEFAULT_COMPANY_LOGO_URL"
          class="w-4 h-4 rounded-full object-contain flex-shrink-0 bg-muted"
          @error="($event.target as HTMLImageElement).style.display = 'none'"
        />
        {{ c.name }}
      </DropdownMenuItem>
    </DropdownMenuContent>
  </DropdownMenu>
</template>
