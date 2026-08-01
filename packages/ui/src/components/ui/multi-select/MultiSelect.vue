<script setup lang="ts">
import { computed, ref } from 'vue'
import { ChevronDown } from 'lucide-vue-next'

import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator
} from '@/components/ui/command'
import type { MultiSelectOption } from './types'

const props = withDefaults(
  defineProps<{
    options: MultiSelectOption[]
    modelValue: string[]
    placeholder?: string
  }>(),
  {
    placeholder: 'Select options'
  }
)

const emit = defineEmits<{
  (e: 'update:modelValue', val: string[]): void
}>()

const isOpen = ref(false)
const search = ref('')

const filteredOptions = computed(() =>
  props.options.filter((opt) => opt.label.toLowerCase().includes(search.value.toLowerCase()))
)

const selectedLabels = computed(() =>
  props.modelValue.map((v) => props.options.find((o) => o.value === v)?.label ?? v)
)

const arraysEqual = (a: string[], b: string[]) =>
  a.length === b.length && a.every((v, i) => v === b[i])

function toggleOption(value: string) {
  const current = [...props.modelValue]
  const updated = current.includes(value)
    ? current.filter((v) => v !== value)
    : [...current, value]
  emit('update:modelValue', updated)
}

function handleClear() {
  if (props.modelValue.length > 0) emit('update:modelValue', [])
}

function toggleAll() {
  const allSorted = props.options.map((opt) => opt.value).sort()
  const current = [...props.modelValue].sort()
  const isAllSelected = arraysEqual(current, allSorted)
  emit('update:modelValue', isAllSelected ? [] : allSorted)
}
</script>

<template>
  <Popover v-model:open="isOpen">
    <PopoverTrigger as-child>
      <Button
        variant="outline"
        class="w-full justify-between font-normal"
        :title="selectedLabels.length > 1 ? selectedLabels.join(', ') : undefined"
      >
        <span v-if="!selectedLabels.length" class="text-muted-foreground text-sm truncate">
          {{ props.placeholder }}
        </span>
        <span v-else-if="selectedLabels.length === 1" class="truncate">{{ selectedLabels[0] }}</span>
        <span v-else class="truncate">…</span>
        <ChevronDown class="w-4 h-4 ml-auto flex-shrink-0" />
      </Button>
    </PopoverTrigger>

    <PopoverContent class="w-[280px] p-0">
      <Command>
        <CommandInput v-model="search" placeholder="Search..." />
        <CommandList>
          <CommandEmpty>No results found.</CommandEmpty>

          <CommandGroup>
            <CommandItem value="__all__" @mousedown.prevent="toggleAll">
              <Checkbox
                class="mr-2 pointer-events-none"
                :checked="props.modelValue.length === props.options.length"
              />
              <span>All</span>
            </CommandItem>

            <CommandItem
              v-for="opt in filteredOptions"
              :key="opt.value"
              :value="opt.value"
              @mousedown.prevent="toggleOption(opt.value)"
            >
              <Checkbox class="mr-2 pointer-events-none" :checked="props.modelValue.includes(opt.value)" />
              <span>{{ opt.label }}</span>
            </CommandItem>
          </CommandGroup>

          <CommandSeparator />

          <CommandGroup>
            <div class="flex items-center justify-between px-2">
              <Button
                v-if="props.modelValue.length"
                variant="ghost"
                size="sm"
                class="text-destructive text-xs"
                @click="handleClear"
              >
                Clear
              </Button>
              <Button variant="ghost" size="sm" class="text-xs ml-auto" @click="isOpen = false">
                Close
              </Button>
            </div>
          </CommandGroup>
        </CommandList>
      </Command>
    </PopoverContent>
  </Popover>
</template>
