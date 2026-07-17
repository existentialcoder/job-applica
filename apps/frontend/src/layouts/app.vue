<script setup lang="ts">
import AppSidebar from '@/components/core/sidebar/AppSidebar.vue';
import AppNavbar from '@/components/core/AppNavbar.vue';
import { useAppStore } from '@/stores/app';

const store = useAppStore();
</script>

<template>
  <div>
    <AppSidebar/>
    <div class="relative app-container app-main" :style="`left: ${store.wrapperLeftOffset}px; width: calc(100% - ${store.wrapperLeftOffset}px)`">
      <AppNavbar />
      <div class="p-2 lg:p-6 max-w-[1440px] m-auto mt-[64px]">
        <RouterView v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component"></component>
          </transition>
        </RouterView>
      </div>
    </div>
  </div>
</template>