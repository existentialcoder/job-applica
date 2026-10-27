<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { Check, ChevronDown, Plus, X } from 'lucide-vue-next'

import { Button } from '@/components/ui/button'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from '@/components/ui/command'
import { cn } from '@/lib/utils'
import type { ComboboxOption } from './types'

const props = withDefaults(
  defineProps<{
    options: ComboboxOption[]
    modelValue: string
    placeholder?: string
    creatable?: boolean
    clearable?: boolean
    class?: string
  }>(),
  {
    placeholder: 'Select…',
    creatable: false,
    clearable: false
  }
)

const emit = defineEmits<{
  (e: 'update:modelValue', val: string): void
}>()

// Leaves every item visible to radix; filteredOptions below does the filtering.
const keepAll = <T,>(list: T): T => list

const isOpen = ref(false)
const search = ref('')

const filteredOptions = computed(() =>
  props.options.filter((opt) => opt.label.toLowerCase().includes(search.value.toLowerCase()))
)

const exactMatch = computed(() =>
  props.options.some((opt) => opt.label.toLowerCase() === search.value.trim().toLowerCase())
)

const selectedLabel = computed(
  () => props.options.find((opt) => opt.value === props.modelValue)?.label || props.modelValue
)

watch(isOpen, (open) => {
  if (!open) search.value = ''
})

function select(value: string) {
  emit('update:modelValue', value)
  isOpen.value = false
}

function createNew() {
  const value = search.value.trim()
  if (!value) return
  select(value)
}
</script>

<template>
  <Popover v-model:open="isOpen">
    <PopoverTrigger as-child>
      <Button
        variant="outline"
        :class="cn('w-full justify-between font-normal', !modelValue && 'text-muted-foreground', props.class)"
      >
        <span class="truncate">{{ modelValue ? selectedLabel : placeholder }}</span>
        <span class="flex shrink-0 items-center ml-auto">
          <!-- A span, not a button: it sits inside the trigger button, and stopping pointerdown keeps the list closed. -->
          <span
            v-if="clearable && modelValue"
            role="button"
            tabindex="0"
            aria-label="Clear"
            class="ml-2 rounded-sm opacity-50 hover:opacity-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            @pointerdown.stop.prevent
            @click.stop="select('')"
            @keydown.enter.stop.prevent="select('')"
          >
            <X class="w-4 h-4" />
          </span>
          <ChevronDown class="w-4 h-4 ml-2 flex-shrink-0 opacity-50" />
        </span>
      </Button>
    </PopoverTrigger>

    <PopoverContent class="w-[280px] p-0">
      <!-- The search text lives on the root (CommandInput's v-model never reaches `search`), and filteredOptions does the
           filtering: radix's own filter would also hide the "Add …" item, whose value never matches the search. -->
      <Command v-model:search-term="search" :filter-function="keepAll">
        <CommandInput placeholder="Search..." />
        <CommandList>
          <CommandEmpty v-if="!creatable">No results found.</CommandEmpty>

          <CommandGroup>
            <CommandItem
              v-for="opt in filteredOptions"
              :key="opt.value"
              :value="opt.value"
              @mousedown.prevent="select(opt.value)"
            >
              <Check
                class="mr-2 h-4 w-4"
                :class="modelValue === opt.value ? 'opacity-100' : 'opacity-0'"
              />
              <span>{{ opt.label }}</span>
            </CommandItem>

            <CommandItem
              v-if="creatable && search.trim() && !exactMatch"
              value="__create__"
              class="text-muted-foreground focus:text-foreground"
              @mousedown.prevent="createNew"
            >
              <Plus class="mr-2 h-4 w-4 flex-shrink-0" />
              <span>Add "{{ search.trim() }}"</span>
            </CommandItem>
          </CommandGroup>
        </CommandList>
      </Command>
    </PopoverContent>
  </Popover>
</template>
