<script setup lang="ts">
withDefaults(defineProps<{
  size?: number
}>(), {
  size: 20
});
</script>

<template>
  <svg :width="size" :height="size" viewBox="0 0 24 24" fill="none">
    <path
      d="M20 4H4a2 2 0 00-2 2v12a2 2 0 002 2h16a2 2 0 002-2V6a2 2 0 00-2-2z"
      stroke="#EA4335"
      stroke-width="1.5"
    />
    <path d="M2 6l10 7 10-7" stroke="#EA4335" stroke-width="1.5" stroke-linecap="round" />
  </svg>
</template>
