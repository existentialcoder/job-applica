<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { Input } from '@/components/ui/input'
import { cn } from '@/lib/utils'
import type { AutocompleteSuggestion } from '.'

// Attributes such as aria-label belong on the input, not the wrapper.
defineOptions({ inheritAttrs: false })

// A text input that lists suggestions under it while the user types. Whatever is typed stays the value; picking a
// suggestion emits `select` and leaves it to the parent to fill the field (and others) from it.
const props = defineProps<{
  modelValue: string
  suggestions: AutocompleteSuggestion[]
  placeholder?: string
  id?: string
  class?: string
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', val: string): void
  (e: 'select', val: string): void
}>()

const listId = `autocomplete-${Math.random().toString(36).slice(2, 9)}`
const focused = ref(false)
const dismissed = ref(false)
// Nothing is highlighted until the user arrows down, so Enter keeps what they typed.
const active = ref(-1)

const open = computed(() => focused.value && !dismissed.value && props.suggestions.length > 0)

watch(() => props.suggestions, () => (active.value = -1))

function onInput(value: string | number) {
  dismissed.value = false
  emit('update:modelValue', String(value))
}

function choose(s: AutocompleteSuggestion) {
  dismissed.value = true
  emit('select', s.value)
}

function onKeydown(e: KeyboardEvent) {
  if (!open.value) return
  const count = props.suggestions.length
  if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
    e.preventDefault()
    active.value = (active.value + (e.key === 'ArrowDown' ? 1 : count - 1)) % count
  } else if (e.key === 'Enter' && active.value >= 0) {
    e.preventDefault()
    choose(props.suggestions[active.value])
  } else if (e.key === 'Escape') {
    dismissed.value = true
  }
}
</script>

<template>
  <div :class="cn('relative', props.class)">
    <Input
      v-bind="$attrs"
      :id="id"
      :model-value="modelValue"
      :placeholder="placeholder"
      autocomplete="off"
      role="combobox"
      aria-autocomplete="list"
      :aria-expanded="open"
      :aria-controls="listId"
      :aria-activedescendant="active >= 0 ? `${listId}-${active}` : undefined"
      @update:model-value="onInput"
      @focus="focused = true"
      @blur="focused = false"
      @keydown="onKeydown"
    />
    <ul
      v-if="open"
      :id="listId"
      role="listbox"
      class="absolute z-50 mt-1 max-h-64 w-full overflow-auto rounded-md border bg-popover p-1 text-popover-foreground shadow-md"
    >
      <li
        v-for="(s, i) in suggestions"
        :id="`${listId}-${i}`"
        :key="s.value"
        role="option"
        :aria-selected="i === active"
        :class="
          cn(
            'flex cursor-default select-none items-center rounded-sm px-2 py-1.5 text-sm',
            i === active && 'bg-primary/10 text-primary'
          )
        "
        @mousemove="active = i"
        @mousedown.prevent="choose(s)"
      >
        {{ s.label }}
      </li>
    </ul>
  </div>
</template>
