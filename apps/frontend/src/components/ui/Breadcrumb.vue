<script setup lang="ts">
import { RouterLink, useRoute } from 'vue-router';
import { computed } from 'vue';

const route = useRoute()
const currentRoute = computed(() => {
  return route.matched.length > 1 ? route.matched[route.matched.length - 1] : route.matched[0];
});

</script>


<template>
  <div class="flex">
    <router-link  :key="currentRoute.path" :to="currentRoute.path">
      <span class="text-sm flex">
        <p :class="route.path === currentRoute.path && 'text-primary font-semibold'">{{ currentRoute.meta.title.split('|')[1] }}</p>
      </span>
    </router-link>
  </div>
</template>
