<script setup lang="ts">
import type { HTMLAttributes } from 'vue'
import { cn } from '@/lib/utils'
import { TimelineDot } from '.'

const props = defineProps<{
  class?: HTMLAttributes['class']
}>()
</script>

<template>
  <li :class="cn('group relative grid grid-cols-[auto_1fr] gap-x-4', props.class)">
    <div class="flex flex-col items-center">
      <slot name="dot">
        <TimelineDot />
      </slot>
      <div class="mt-1 w-px flex-1 bg-border group-last:hidden" />
    </div>
    <div class="pb-8 pt-0.5 group-last:pb-0">
      <slot />
    </div>
  </li>
</template>
