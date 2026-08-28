<script setup lang="ts">
import { DewLogo } from '@job-applica/ui';

withDefaults(
  defineProps<{
    collapsed?: boolean
    showBrandName?: boolean
  }>(),
  {
    collapsed: false,
    showBrandName: true
  }
);
</script>

<template>
  <DewLogo
    :size="32"
    :show-wordmark="showBrandName && !collapsed"
    wordmark-color="hsl(var(--foreground))"
    class="select-none"
  />
</template>
