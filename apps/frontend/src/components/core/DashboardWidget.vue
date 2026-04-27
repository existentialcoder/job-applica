<script setup lang="ts">
import { ref } from 'vue';
import { Maximize2, X } from 'lucide-vue-next';
import { Dialog, DialogContent } from '@/components/ui/dialog';

defineProps<{
  title: string
  subtitle?: string
}>();

const emit = defineEmits<{ remove: [] }>();

const isExpanded = ref(false);
</script>

<template>
  <!-- Card view -->
  <div class="rounded-xl border bg-card p-5 flex flex-col gap-4">
    <div class="flex items-start justify-between">
      <div class="min-w-0">
        <h2 class="font-semibold text-sm">{{ title }}</h2>
        <p v-if="subtitle" class="text-xs text-muted-foreground mt-0.5">{{ subtitle }}</p>
      </div>
      <div class="flex items-center gap-0.5 ml-3 flex-shrink-0">
        <button
          @click="isExpanded = true"
          class="p-1.5 rounded hover:bg-muted transition-colors text-muted-foreground hover:text-foreground"
          title="Expand"
        >
          <Maximize2 class="w-3.5 h-3.5" />
        </button>
        <button
          @click="emit('remove')"
          class="p-1.5 rounded hover:bg-muted transition-colors text-muted-foreground hover:text-destructive"
          title="Remove widget"
        >
          <X class="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
    <slot :expanded="false" />
  </div>

  <!-- Expanded dialog -->
  <Dialog :open="isExpanded" @update:open="(v) => !v && (isExpanded = false)">
    <DialogContent class="max-w-3xl w-full p-0 gap-0">
      <div class="p-6 flex flex-col gap-5">
        <div>
          <h2 class="font-semibold text-base">{{ title }}</h2>
          <p v-if="subtitle" class="text-sm text-muted-foreground mt-0.5">{{ subtitle }}</p>
        </div>
        <slot :expanded="true" />
      </div>
    </DialogContent>
  </Dialog>
</template>
