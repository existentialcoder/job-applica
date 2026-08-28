<script setup lang="ts">
import { computed } from 'vue';

const props = withDefaults(defineProps<{
  percentage?: number
  size?: number
  strokeWidth?: number
  color?: string
  showValue?: boolean
}>(), {
  size: 96,
  strokeWidth: 8,
  color: 'currentColor',
  showValue: true
});

const RADIUS = 42;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;

const dashOffset = computed(() => {
  if (props.percentage == null) return CIRCUMFERENCE;
  return CIRCUMFERENCE - (props.percentage / 100) * CIRCUMFERENCE;
});
</script>

<template>
  <div :style="{ position: 'relative', width: `${size}px`, height: `${size}px`, flexShrink: 0 }">
    <svg :width="size" :height="size" viewBox="0 0 100 100" style="transform: rotate(-90deg)">
      <circle
        cx="50"
        cy="50"
        r="42"
        fill="none"
        stroke="currentColor"
        :stroke-width="strokeWidth"
        style="opacity:0.3"
      />
      <circle
        v-if="percentage != null"
        cx="50"
        cy="50"
        r="42"
        fill="none"
        :stroke="color"
        :stroke-width="strokeWidth"
        stroke-linecap="round"
        :stroke-dasharray="CIRCUMFERENCE"
        :stroke-dashoffset="dashOffset"
        style="transition: stroke-dashoffset 0.6s ease"
      />
    </svg>
    <div
      style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center"
    >
      <slot>
        <template v-if="showValue && percentage != null">
          <span :style="{ fontSize: `${Math.round(size * 0.23)}px`, fontWeight: 700, lineHeight: 1 }">{{ Math.round(percentage) }}</span>
        </template>
      </slot>
    </div>
  </div>
</template>
