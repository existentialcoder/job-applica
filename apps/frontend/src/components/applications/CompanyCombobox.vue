<script setup lang="ts">
import { computed, ref, watch, nextTick } from 'vue'
import { Check, ChevronDown, Plus, X } from 'lucide-vue-next'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger
} from '@/components/ui/dropdown-menu'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { cn } from '@/lib/utils'
import { DEFAULT_COMPANY_LOGO_URL } from '@/lib/constants'
import type { CompanyOption } from '@/stores/companies'

const props = defineProps<{
  modelValue: string
  companies: CompanyOption[]
  placeholder?: string
  class?: string
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', val: string): void
}>()

const open = ref(false)
const addingNewCompany = ref(false)
const newName = ref('')

watch(open, (val) => {
  if (!val) {
    addingNewCompany.value = false
    newName.value = ''
  }
})

function select(name: string) {
  emit('update:modelValue', name)
  open.value = false
}

async function startAddingCompany() {
  addingNewCompany.value = true
  newName.value = ''
  await nextTick()
}

async function confirmAdd() {
  const name = newName.value.trim()
  if (!name) {
    return
  }
  emit('update:modelValue', name)
  await nextTick()
  addingNewCompany.value = false
  newName.value = ''
  open.value = false
}

async function cancelAdd() {
  await nextTick()
  addingNewCompany.value = false
  newName.value = ''
}

const selectedLogo = computed(() => {
  return (
    props.companies.find((c) => c.name === props.modelValue)?.logo_url || DEFAULT_COMPANY_LOGO_URL
  )
})
</script>

<template>
  <DropdownMenu v-model:open="open">
    <DropdownMenuTrigger as-child>
      <Button
        variant="outline"
        :class="
          cn(
            'w-full justify-between font-normal h-9 px-3',
            !modelValue && 'text-muted-foreground',
            props.class
          )
        "
      >
        <span class="flex items-center gap-2 min-w-0">
          <!-- Selected company logo -->
          <img
            v-if="modelValue"
            :src="selectedLogo"
            class="h-5 w-5 rounded-full object-contain shrink-0 bg-muted"
            @error="($event.target as HTMLImageElement).style.display = 'none'"
          />
          <svg
            v-else
            class="h-4 w-4 shrink-0 opacity-50"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            stroke-width="1.5"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M3.75 21h16.5M4.5 3h15M5.25 3v18m13.5-18v18M9 6.75h1.5m-1.5 3h1.5m-1.5 3h1.5m3-6H15m-1.5 3H15m-1.5 3H15M9 21v-3.375c0-.621.504-1.125 1.125-1.125h3.75c.621 0 1.125.504 1.125 1.125V21"
            />
          </svg>
          <span class="truncate">{{ modelValue || (placeholder ?? 'Select company') }}</span>
        </span>
        <ChevronDown class="h-4 w-4 shrink-0 opacity-50" />
      </Button>
    </DropdownMenuTrigger>

    <DropdownMenuContent class="w-[240px]" align="start">
      <!-- Empty state -->
      <p
        v-if="!companies.length && !addingNewCompany"
        class="py-3 text-center text-xs text-muted-foreground"
      >
        No companies yet
      </p>

      <!-- Company list -->
      <DropdownMenuItem
        v-for="c in companies"
        :key="c.id"
        :class="cn('gap-2 cursor-pointer', modelValue === c.name && 'font-medium')"
        @click="select(c.name)"
      >
        <img
          :src="c.logo_url || DEFAULT_COMPANY_LOGO_URL"
          class="h-5 w-5 rounded-full object-contain shrink-0 bg-muted"
          @error="($event.target as HTMLImageElement).style.display = 'none'"
        />
        <span class="flex-1 truncate">{{ c.name }}</span>
        <Check v-if="modelValue === c.name" class="h-4 w-4 shrink-0 text-primary" />
      </DropdownMenuItem>

      <DropdownMenuSeparator v-if="companies.length" />

      <!-- Add company trigger -->
      <div
        v-if="!addingNewCompany"
        class="relative flex select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none transition-colors gap-2 cursor-pointer text-muted-foreground hover:bg-accent hover:text-foreground focus:bg-primary/10 focus:text-foreground"
        @click="startAddingCompany"
      >
        <Plus class="h-3.5 w-3.5 shrink-0" />
        Add company
      </div>
      <!-- Inline add form -->
      <div v-else class="flex items-center gap-1.5 px-1 py-1" @click.stop @keydown.stop>
        <Input
          ref="newNameRef"
          v-model="newName"
          class="h-7 flex-1 text-sm"
          placeholder="Company name"
          @keyup.enter="confirmAdd"
          @keyup.escape="cancelAdd"
        />
        <Button
          variant="ghost"
          size="icon"
          class="h-7 w-7 shrink-0 text-green-600 hover:text-green-600 hover:bg-green-50 dark:hover:bg-green-950"
          title="Confirm"
          @click.stop="confirmAdd"
        >
          <Check class="h-3.5 w-3.5" />
        </Button>
        <Button
          variant="ghost"
          size="icon"
          class="h-7 w-7 shrink-0 text-destructive hover:text-destructive hover:bg-destructive/10"
          title="Cancel"
          @click.stop="cancelAdd"
        >
          <X class="h-3.5 w-3.5" />
        </Button>
      </div>
    </DropdownMenuContent>
  </DropdownMenu>
</template>
