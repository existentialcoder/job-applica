<script setup lang="ts">
import { Toggle } from '@/components/ui/toggle'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import router from '@/router'
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { APP_MENU } from '@/config/app'
import { ArrowLeftToLine } from 'lucide-vue-next'
import { useAppStore } from '@/stores/app'
import AppLogo from '@/components/core/AppLogo.vue'

const route = useRoute()

const menus = APP_MENU

const handleNavigate = (path: string) => {
  router.push(path)
  if (window.innerWidth < 1025) {
    store.toggleSidebar()
  }
}

const store = useAppStore()

const toggleSidebar = () => {
  store.toggleSidebar()
}
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
            :class="store.sidebarExpanded ? 'justify-between' : 'justify-center'"
            :style="{ width: `${store.sidebarExpanded ? 280 : 64}px` }"
          >
            <!-- Collapsed: logo icon is the expand trigger -->
            <button
              v-if="!store.sidebarExpanded"
              class="cursor-pointer rounded-md p-0.5 hover:opacity-80 transition-opacity"
              @click="toggleSidebar"
              aria-label="Expand sidebar"
            >
              <AppLogo :collapsed="true" />
            </button>

            <!-- Expanded: full logo + collapse button -->
            <template v-else>
              <AppLogo :collapsed="false" />
              <Button
                variant="outline"
                class="p-[6px] w-8 h-8 flex-shrink-0 bg-transparent transition-all duration-200"
                @click="toggleSidebar"
              >
                <ArrowLeftToLine class="transition-all duration-500" />
              </Button>
            </template>
          </div>
        </div>

        <!-- Scrollable menu -->
        <ScrollArea style="height: calc(100vh - 64px)">
          <div class="transition-all" :class="store.sidebarExpanded ? 'p-4' : 'p-2'">
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
                        class="w-full overflow-x-hidden justify-start duration-150"
                        :pressed="route.path.startsWith(menu.path)"
                        @click="handleNavigate(menu.path)"
                      >
                        <span
                          class="flex items-center"
                          :class="store.sidebarExpanded ? 'mr-4' : 'm-0'"
                        >
                          <Icon :name="menu.icon" />
                        </span>
                        <transition name="fade" :duration="300">
                          <span v-show="store.sidebarExpanded">{{ menu.title }}</span>
                        </transition>
                      </Toggle>
                    </TooltipTrigger>
                    <template v-if="!store.sidebarExpanded">
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

      <!-- Footer -->
      <div
        class="border-t-[1px] transition-all duration-400 py-4"
        :class="store.sidebarExpanded ? 'opacity-100' : 'opacity-0'"
      >
        <p class="text-xs text-foreground/50 text-center">&copy; 2024 Dashcn</p>
      </div>
    </div>
  </div>
</template>
