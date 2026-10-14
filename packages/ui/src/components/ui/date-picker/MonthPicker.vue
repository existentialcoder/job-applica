<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { Calendar as CalendarIcon, ChevronLeft, ChevronRight, X } from 'lucide-vue-next'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

const props = defineProps<{
  modelValue?: string | null // YYYY-MM
  placeholder?: string
  disabled?: boolean
  class?: string
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', val: string): void
}>()

const MONTHS = Array.from({ length: 12 }, (_, i) =>
  new Intl.DateTimeFormat('en-US', { month: 'short' }).format(new Date(2000, i, 1))
)

const open = ref(false)

const selected = computed(() => {
  const [y, m] = (props.modelValue ?? '').split('-').map(Number)
  return y && m ? { year: y, month: m } : undefined
})

const year = ref(selected.value?.year ?? new Date().getFullYear())
// Reopening starts from the chosen year, not wherever the user last browsed to.
watch(open, (isOpen) => {
  if (isOpen) year.value = selected.value?.year ?? new Date().getFullYear()
})

const displayDate = computed(() =>
  selected.value ? `${MONTHS[selected.value.month - 1]} ${selected.value.year}` : ''
)

function pick(month: number) {
  emit('update:modelValue', `${year.value}-${String(month).padStart(2, '0')}`)
  open.value = false
}

function clear() {
  emit('update:modelValue', '')
}
</script>

<template>
  <div :class="cn('flex items-center gap-1', props.class)">
    <Popover v-model:open="open">
      <PopoverTrigger as-child>
        <Button
          variant="outline"
          :disabled="disabled"
          :class="
            cn(
              'flex-1 justify-start text-left font-normal h-10 px-3 gap-2',
              !modelValue && 'text-muted-foreground'
            )
          "
        >
          <CalendarIcon class="h-4 w-4 shrink-0 opacity-50" />
          <span>{{ displayDate || (placeholder ?? 'Pick a month') }}</span>
        </Button>
      </PopoverTrigger>
      <PopoverContent class="w-64 p-3" align="start">
        <div class="flex items-center justify-between pb-2">
          <Button variant="outline" size="icon" class="h-7 w-7" aria-label="Previous year" @click="year--">
            <ChevronLeft class="h-4 w-4" />
          </Button>
          <span class="text-sm font-medium" aria-live="polite">{{ year }}</span>
          <Button variant="outline" size="icon" class="h-7 w-7" aria-label="Next year" @click="year++">
            <ChevronRight class="h-4 w-4" />
          </Button>
        </div>
        <div class="grid grid-cols-3 gap-1">
          <Button
            v-for="(label, i) in MONTHS"
            :key="label"
            :variant="selected?.year === year && selected.month === i + 1 ? 'default' : 'ghost'"
            size="sm"
            class="font-normal"
            :aria-pressed="selected?.year === year && selected.month === i + 1"
            @click="pick(i + 1)"
          >
            {{ label }}
          </Button>
        </div>
      </PopoverContent>
    </Popover>

    <Button
      v-if="modelValue && !disabled"
      variant="ghost"
      size="icon"
      class="h-10 w-10 shrink-0 text-muted-foreground hover:text-foreground"
      title="Clear month"
      aria-label="Clear month"
      @click="clear"
    >
      <X class="h-4 w-4" />
    </Button>
  </div>
</template>
