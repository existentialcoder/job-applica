<script setup lang="ts">
const t = useT()
</script>

<template>
  <div class="platforms" :aria-label="`${t.platforms.label} ${t.platforms.items.join(', ')}`">
    <div class="container">
      <div class="platforms-inner">
        <span class="platforms-label">{{ t.platforms.label }}</span>
        <template v-for="(platform, i) in t.platforms.items" :key="platform">
          <span class="platform-pill">{{ platform }}</span>
          <span v-if="i < t.platforms.items.length - 1" class="platform-dot" aria-hidden="true"></span>
        </template>
      </div>
    </div>
  </div>
</template>
