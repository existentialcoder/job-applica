<script setup lang="ts">
import { Badge } from '@/components/ui/badge';

defineProps<{
  color?: string;
  label?: string;
}>();
</script>

<template>
  <Badge variant="outline" class="gap-1.5 min-w-0 max-w-full">
    <span v-if="color" class="w-1.5 h-1.5 rounded-full flex-shrink-0" :class="color" />
    <slot>{{ label }}</slot>
  </Badge>
</template>
