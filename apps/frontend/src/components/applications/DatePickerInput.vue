<script setup lang="ts">
import { computed, ref } from 'vue';
import { Calendar as CalendarIcon, X } from 'lucide-vue-next';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Button } from '@/components/ui/button';
import { Calendar } from '@/components/ui/calendar';
import { cn } from '@/lib/utils';

const props = defineProps<{
  modelValue?: string   // YYYY-MM-DD
  placeholder?: string
  class?: string
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', val: string): void
}>();

const open = ref(false);

function parseDate(str: string): Date | undefined {
  if (!str) return undefined;
  const [y, m, d] = str.split('-').map(Number);
  const date = new Date(y, m - 1, d);
  return isNaN(date.getTime()) ? undefined : date;
}

const internalDate = computed(() => parseDate(props.modelValue ?? ''));

const displayDate = computed(() => {
  if (!internalDate.value) return '';
  return new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric', year: 'numeric' }).format(internalDate.value);
});

function onSelect(val: unknown) {
  if (!val) return;
  const d = val instanceof Date ? val : new Date(val as string | number);
  if (isNaN(d.getTime())) return;
  const yyyy = d.getFullYear();
  const mm = String(d.getMonth() + 1).padStart(2, '0');
  const dd = String(d.getDate()).padStart(2, '0');
  emit('update:modelValue', `${yyyy}-${mm}-${dd}`);
  open.value = false;
}

function clear() {
  emit('update:modelValue', '');
}
</script>

<template>
  <div :class="cn('flex items-center gap-1', props.class)">
    <Popover v-model:open="open">
      <PopoverTrigger as-child>
        <Button
          variant="outline"
          :class="cn(
            'flex-1 justify-start text-left font-normal h-9 px-3 gap-2',
            !modelValue && 'text-muted-foreground',
          )"
        >
          <CalendarIcon class="h-4 w-4 shrink-0 opacity-50" />
          <span>{{ displayDate || (placeholder ?? 'Pick a date') }}</span>
        </Button>
      </PopoverTrigger>
      <PopoverContent class="w-auto p-0" align="start">
        <Calendar :model-value="internalDate" @update:model-value="onSelect" />
      </PopoverContent>
    </Popover>

    <Button
      v-if="modelValue"
      variant="ghost"
      size="icon"
      class="h-9 w-9 shrink-0 text-muted-foreground hover:text-foreground"
      title="Clear date"
      @click="clear"
    >
      <X class="h-4 w-4" />
    </Button>
  </div>
</template>
