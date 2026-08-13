<script setup lang="ts">
import { computed, ref } from 'vue'
import { Calendar as CalendarIcon, X } from 'lucide-vue-next'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { Button } from '@/components/ui/button'
import { Calendar } from '@/components/ui/calendar'
import { cn } from '@/lib/utils'

const props = defineProps<{
  modelValue?: { from: string; to: string } // both YYYY-MM-DD
  placeholder?: string
  class?: string
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', val: { from: string; to: string }): void
}>()

const open = ref(false)

function parseDate(str: string | undefined): Date | undefined {
  if (!str) return undefined
  const [y, m, d] = str.split('-').map(Number)
  const date = new Date(y, m - 1, d)
  return isNaN(date.getTime()) ? undefined : date
}

function formatDate(date: Date): string {
  const yyyy = date.getFullYear()
  const mm = String(date.getMonth() + 1).padStart(2, '0')
  const dd = String(date.getDate()).padStart(2, '0')
  return `${yyyy}-${mm}-${dd}`
}

function formatDisplay(date: Date): string {
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  }).format(date)
}

const internalRange = computed({
  get: () => {
    const start = parseDate(props.modelValue?.from)
    const end = parseDate(props.modelValue?.to)
    return start && end ? { start, end } : undefined
  },
  set: (val: { start?: Date; end?: Date } | null) => {
    if (!val?.start || !val?.end) return
    emit('update:modelValue', { from: formatDate(val.start), to: formatDate(val.end) })
    open.value = false
  }
})

const displayText = computed(() => {
  const start = parseDate(props.modelValue?.from)
  const end = parseDate(props.modelValue?.to)
  return start && end ? `${formatDisplay(start)} – ${formatDisplay(end)}` : ''
})

function clear() {
  emit('update:modelValue', { from: '', to: '' })
}
</script>

<template>
  <div :class="cn('flex items-center gap-1', props.class)">
    <Popover v-model:open="open">
      <PopoverTrigger as-child>
        <Button
          variant="outline"
          :class="
            cn(
              'flex-1 justify-start text-left font-normal h-9 px-3 gap-2',
              !displayText && 'text-muted-foreground'
            )
          "
        >
          <CalendarIcon class="h-4 w-4 shrink-0 opacity-50" />
          <span>{{ displayText || (placeholder ?? 'Pick a date range') }}</span>
        </Button>
      </PopoverTrigger>
      <PopoverContent class="w-auto p-0" align="start">
        <Calendar v-model.range="internalRange" :columns="2" />
      </PopoverContent>
    </Popover>

    <Button
      v-if="displayText"
      variant="ghost"
      size="icon"
      class="h-9 w-9 shrink-0 text-muted-foreground hover:text-foreground"
      title="Clear date range"
      @click="clear"
    >
      <X class="h-4 w-4" />
    </Button>
  </div>
</template>
