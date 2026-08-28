<script setup lang="ts">
import { ArrowLeftToLine, ChevronRight } from 'lucide-vue-next';
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import AppLogo from '@/components/core/AppLogo.vue';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Toggle } from '@/components/ui/toggle';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { ALL_MENU_ITEMS, SETTINGS_MENU_ITEM } from '@/config/app';
import router from '@/router';
import { useAppStore } from '@/stores/app';
import { useFeatureStore } from '@/stores/features';
import { useSettingsStore } from '@/stores/settings';

const route = useRoute();
const featureStore = useFeatureStore();

const menus = computed(() => ALL_MENU_ITEMS.filter((m) => !m.flag || featureStore.flags[m.flag]));

const handleNavigate = (path: string) => {
  router.push(path);
  if (window.innerWidth < 1025) {
    settingsStore.toggleSidebar();
  }
};

const store = useAppStore();
const settingsStore = useSettingsStore();

const toggleSidebar = () => {
  settingsStore.toggleSidebar();
};
</script>

<template>
  <div
    class="sidebar transition-all duration-400 h-screen overflow-hidden bg-background border-r-[1px] fixed"
    :style="{ width: `${store.wrapperWidth}px` }"
  >
    <div class="relative h-full flex flex-col justify-between">
      <div>
        <!-- Header -->
        <div class="h-[64px]">
          <div
            class="px-4 h-[64px] flex fixed z-10 items-center border-b-[1px]"
            :class="settingsStore.settings.sidebarExpanded ? 'justify-between' : 'justify-center'"
            :style="{ width: `${settingsStore.settings.sidebarExpanded ? 280 : 64}px` }"
          >
            <button
              v-if="!settingsStore.settings.sidebarExpanded"
              class="cursor-pointer rounded-md p-0.5 hover:opacity-80 transition-opacity"
              @click="handleNavigate('/home')"
              aria-label="Go to home"
            >
              <AppLogo :collapsed="true" />
            </button>

            <template v-else>
              <button
                class="cursor-pointer rounded-md hover:opacity-80 transition-opacity"
                @click="handleNavigate('/home')"
                aria-label="Go to home"
              >
                <AppLogo :collapsed="false" />
              </button>
              <button
                class="flex-shrink-0 cursor-pointer text-muted-foreground hover:text-foreground transition-colors"
                @click="toggleSidebar"
                aria-label="Collapse sidebar"
              >
                <ArrowLeftToLine class="w-5 h-5 transition-all duration-500" />
              </button>
            </template>
          </div>

          <!-- Collapsed: dedicated expand trigger, anchored at the sidebar edge near the logo -->
          <button
            v-if="!settingsStore.settings.sidebarExpanded"
            class="absolute right-2 top-6 z-20 flex items-center justify-center text-muted-foreground hover:text-foreground transition-colors"
            @click="toggleSidebar"
            aria-label="Expand sidebar"
          >
            <ChevronRight class="w-3.5 h-3.5" />
          </button>
        </div>

        <!-- Scrollable menu -->
        <ScrollArea style="height: calc(100vh - 64px - 72px)">
          <div class="transition-all" :class="settingsStore.settings.sidebarExpanded ? 'p-4' : 'p-2'">
            <ul>
              <li
                v-for="menu in menus"
                :key="`${menu.title}-${menu.path}`"
                class="flex items-center mb-5 rounded-md"
              >
                <TooltipProvider :disable-hoverable-content="true">
                  <Tooltip :delay-duration="0">
                    <TooltipTrigger class="w-full">
                      <Toggle
                        class="w-full overflow-x-hidden justify-start duration-150 hover:bg-primary/10 hover:text-primary data-[state=on]:bg-primary/15 data-[state=on]:text-primary"
                        :pressed="route.path.startsWith(menu.path)"
                        @click="handleNavigate(menu.path)"
                      >
                        <span
                          class="flex items-center"
                          :class="settingsStore.settings.sidebarExpanded ? 'mr-4' : 'm-0'"
                        >
                          <Icon :name="menu.icon" />
                        </span>
                        <transition name="fade" :duration="300">
                          <span v-show="settingsStore.settings.sidebarExpanded">{{ menu.title }}</span>
                        </transition>
                      </Toggle>
                    </TooltipTrigger>
                    <template v-if="!settingsStore.settings.sidebarExpanded">
                      <TooltipContent side="right">
                        <p class="text-sm">{{ menu.title }}</p>
                      </TooltipContent>
                    </template>
                  </Tooltip>
                </TooltipProvider>
              </li>
            </ul>
          </div>
        </ScrollArea>
      </div>

      <!-- Bottom: Settings pinned -->
      <div
        class="border-t-[1px] transition-all duration-400"
        :class="settingsStore.settings.sidebarExpanded ? 'p-4' : 'p-2'"
      >
        <TooltipProvider :disable-hoverable-content="true">
          <Tooltip :delay-duration="0">
            <TooltipTrigger class="w-full">
              <Toggle
                class="w-full overflow-x-hidden justify-start duration-150 hover:bg-primary/10 hover:text-primary data-[state=on]:bg-primary/15 data-[state=on]:text-primary"
                :pressed="route.path.startsWith(SETTINGS_MENU_ITEM.path)"
                @click="handleNavigate(SETTINGS_MENU_ITEM.path)"
              >
                <span class="flex items-center" :class="settingsStore.settings.sidebarExpanded ? 'mr-4' : 'm-0'">
                  <Icon :name="SETTINGS_MENU_ITEM.icon" />
                </span>
                <transition name="fade" :duration="300">
                  <span v-show="settingsStore.settings.sidebarExpanded">{{ SETTINGS_MENU_ITEM.title }}</span>
                </transition>
              </Toggle>
            </TooltipTrigger>
            <template v-if="!settingsStore.settings.sidebarExpanded">
              <TooltipContent side="right">
                <p class="text-sm">{{ SETTINGS_MENU_ITEM.title }}</p>
              </TooltipContent>
            </template>
          </Tooltip>
        </TooltipProvider>
      </div>
    </div>
  </div>
</template>
