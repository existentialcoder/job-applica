<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { Check, ChevronDown, Plus } from 'lucide-vue-next'

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
    class?: string
  }>(),
  {
    placeholder: 'Select…',
    creatable: false
  }
)

const emit = defineEmits<{
  (e: 'update:modelValue', val: string): void
}>()

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
        <ChevronDown class="w-4 h-4 ml-2 flex-shrink-0 opacity-50" />
      </Button>
    </PopoverTrigger>

    <PopoverContent class="w-[280px] p-0">
      <Command>
        <CommandInput v-model="search" placeholder="Search..." />
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
