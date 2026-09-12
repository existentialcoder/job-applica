<script setup lang="ts">
import type { HTMLAttributes } from 'vue'
import { type TimelineDotVariants, timelineDotVariants } from '.'
import { cn } from '@/lib/utils'

const props = defineProps<{
  variant?: TimelineDotVariants['variant']
  size?: TimelineDotVariants['size']
  class?: HTMLAttributes['class']
}>()
</script>

<template>
  <div :class="cn(timelineDotVariants({ variant, size }), props.class)">
    <slot />
  </div>
</template>
