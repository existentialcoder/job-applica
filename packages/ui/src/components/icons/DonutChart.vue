<script setup lang="ts">
import { computed } from 'vue';

const props = withDefaults(defineProps<{
  segments: { value: number, color: string }[]
  size?: number
  strokeWidth?: number
}>(), {
  size: 128,
  strokeWidth: 16
});

const RADIUS = 54;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;

const computedSegments = computed(() => {
  const total = props.segments.reduce((sum, s) => sum + s.value, 0) || 1;
  let offset = 0;
  return props.segments
    .filter((s) => s.value > 0)
    .map((s) => {
      const dash = (s.value / total) * CIRCUMFERENCE;
      const seg = { ...s, dash, offset };
      offset += dash;
      return seg;
    });
});
</script>

<template>
  <svg :width="size" :height="size" viewBox="0 0 128 128" style="transform: rotate(-90deg)">
    <circle
      cx="64"
      cy="64"
      r="54"
      fill="none"
      stroke="currentColor"
      :stroke-width="strokeWidth"
      style="opacity:0.3"
    />
    <circle
      v-for="(seg, i) in computedSegments"
      :key="i"
      cx="64"
      cy="64"
      r="54"
      fill="none"
      :stroke="seg.color"
      :stroke-width="strokeWidth"
      :stroke-dasharray="`${seg.dash} ${CIRCUMFERENCE - seg.dash}`"
      :stroke-dashoffset="-seg.offset"
    />
  </svg>
</template>
