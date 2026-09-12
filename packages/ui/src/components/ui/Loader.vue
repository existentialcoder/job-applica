<script setup lang="ts">
import { LoaderCircle } from 'lucide-vue-next';

withDefaults(defineProps<{ size?: number; variant?: 'dew' | 'spin' }>(), {
  size: 24,
  variant: 'spin'
});

defineOptions({ inheritAttrs: false });
</script>

<template>
  <svg
    v-if="variant === 'dew'"
    class="dew-loader"
    :width="size"
    :height="size"
    viewBox="20 0 432 480"
    xmlns="http://www.w3.org/2000/svg"
    aria-hidden="true"
    v-bind="$attrs"
  >
    <defs>
      <linearGradient id="dew-loader-grad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="#4F46E5" />
        <stop offset="100%" stop-color="#7C3AED" />
      </linearGradient>
    </defs>
    <path fill="url(#dew-loader-grad)" d="M 430,112 C 452,222 362,470 230,470 A 200,200 0 0 1 30,270 C 30,78 172,8 430,112 Z" />
    <g class="dew-loader-inner">
      <circle cx="248" cy="154" r="22" fill="white" />
      <path fill="white" d="M 231,194 L 265,194 L 265,360 Q 265,442 210,442 Q 172,442 172,406 L 172,388 Q 172,418 210,418 Q 248,418 248,360 L 248,194 Z" />
    </g>
  </svg>

  <LoaderCircle v-else :size="size" :stroke-width="1.5" class="animate-spin" aria-hidden="true" v-bind="$attrs" />
</template>

<style scoped>
.dew-loader {
  display: inline-block;
  transform-origin: 50% 52%;
  animation: dew-loader-wobble 1s infinite;
  filter: drop-shadow(0 0 4px hsl(var(--primary) / 0.35));
}

.dew-loader-inner {
  transform-box: fill-box;
  transform-origin: 50% 50%;
  animation: dew-loader-inner-wobble 1s infinite;
}

@keyframes dew-loader-wobble {
  20% {
    transform: rotate(-18deg);
  }
  75% {
    transform: rotate(380deg);
  }
  80%,
  100% {
    transform: rotate(360deg);
  }
}

@keyframes dew-loader-inner-wobble {
  20% {
    transform: rotate(12deg);
  }
  60% {
    transform: rotate(-26deg);
  }
  80%,
  100% {
    transform: rotate(0deg);
  }
}

@media (prefers-reduced-motion: reduce) {
  .dew-loader,
  .dew-loader-inner {
    animation-duration: 3.5s;
  }
}
</style>
