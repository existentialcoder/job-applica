<script setup lang="ts">
withDefaults(defineProps<{
  size?: number
}>(), {
  size: 20
});
</script>

<template>
  <svg :width="size" :height="size" viewBox="0 0 24 24" fill="none">
    <rect x="3" y="4" width="18" height="17" rx="2" stroke="#4285F4" stroke-width="1.5" />
    <path d="M3 9h18" stroke="#4285F4" stroke-width="1.5" />
    <path d="M8 2v4M16 2v4" stroke="#4285F4" stroke-width="1.5" stroke-linecap="round" />
  </svg>
</template>
