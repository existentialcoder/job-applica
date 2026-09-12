<script setup lang="ts">
import type { HTMLAttributes } from 'vue'
import { cn } from '@/lib/utils'

const props = defineProps<{
  datetime?: string
  class?: HTMLAttributes['class']
}>()
</script>

<template>
  <time :datetime="datetime" :class="cn('text-xs font-medium text-muted-foreground', props.class)">
    <slot />
  </time>
</template>
