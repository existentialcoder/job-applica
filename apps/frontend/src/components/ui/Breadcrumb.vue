<script setup lang="ts">
import { RouterLink, useRoute } from 'vue-router';
import { onUpdated } from 'vue';
import { computed } from 'vue';

const route = useRoute()
const currentRoute = computed(() => {
  return route.matched[1]
});

</script>


<template>
  <div class="flex">
    <router-link  :key="currentRoute.path" :to="currentRoute.path">
      <span class="text-sm flex">
        <p :class="route.path === currentRoute.path && 'text-primary font-semibold'">{{ currentRoute.meta.title }}</p>
      </span>
    </router-link>
  </div>
</template>
