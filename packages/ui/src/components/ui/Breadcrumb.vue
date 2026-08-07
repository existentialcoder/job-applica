<script setup lang="ts">
import { RouterLink, useRoute } from 'vue-router'
import { computed } from 'vue'

export interface BreadcrumbItem {
  label: string
  path?: string
}

const props = defineProps<{
  breadcrumbs?: BreadcrumbItem[]
}>()

const route = useRoute()

const currentRoute = computed(() => {
  return route.matched.length > 1 ? route.matched[route.matched.length - 1] : route.matched[0]
})

const hasBreadcrumbs = computed(() => (props.breadcrumbs?.length ?? 0) > 0)
</script>

<template>
  <div class="flex items-center gap-1 text-md">
    <!-- Dynamic multi-level breadcrumbs (passed in by the consuming app) -->
    <template v-if="hasBreadcrumbs">
      <template v-for="(crumb, i) in breadcrumbs" :key="i">
        <span v-if="i > 0" class="text-muted-foreground/50 mx-0.5">/</span>
        <router-link
          v-if="crumb.path && i < breadcrumbs!.length - 1"
          :to="crumb.path"
          class="text-muted-foreground hover:text-foreground transition-colors"
        >
          {{ crumb.label }}
        </router-link>
        <span v-else class="text-primary font-semibold">{{ crumb.label }}</span>
      </template>
    </template>

    <!-- Default: single route title -->
    <template v-else>
      <router-link :key="currentRoute.path" :to="currentRoute.path">
        <span :class="route.path === currentRoute.path && 'text-primary font-semibold'">
          {{ (currentRoute.meta.title as string)?.split('|')[1] }}
        </span>
      </router-link>
    </template>
  </div>
</template>
