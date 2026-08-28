<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger
} from '@/components/ui/dropdown-menu';
import type { BoardData } from '@/lib/types';
import { useAppStore } from '@/stores/app';
import { useBoardsStore } from '@/stores/boards';
import Applications from '@/views/Applications.vue';

const router = useRouter();
const appStore = useAppStore();
const boardsStore = useBoardsStore();

const isBoardSwitcherOpen = ref(false);

function switchBoard(target: BoardData) {
  isBoardSwitcherOpen.value = false;
  router.push(`/boards/${target.id}`);
}

onMounted(async () => {
  appStore.setBreadcrumbs([{ label: 'Boards', path: '/boards' }, { label: 'All Applications' }]);
});

onUnmounted(() => {
  appStore.setBreadcrumbs([]);
});
</script>

<template>
  <div class="flex flex-col gap-4">
    <div class="flex items-center justify-between gap-3">
      <div class="flex items-center gap-3 min-w-0 flex-1">
        <div class="w-3 h-3 rounded-full flex-shrink-0 bg-muted-foreground/40" />
        <div class="min-w-0">
          <DropdownMenu v-model:open="isBoardSwitcherOpen">
            <DropdownMenuTrigger as-child>
              <button
                type="button"
                class="group -ml-1.5 px-1.5 py-0.5 rounded-md cursor-pointer text-left"
              >
                <span class="flex items-center gap-1.5">
                  <h1 class="text-xl font-semibold truncate">All Applications</h1>
                  <Icon
                    name="ChevronDown"
                    class="w-4 h-4 text-muted-foreground flex-shrink-0 transition-all opacity-0 group-hover:opacity-100 group-focus-visible:opacity-100"
                    :class="{ 'rotate-180 opacity-100': isBoardSwitcherOpen }"
                  />
                </span>
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="start" class="w-56">
              <DropdownMenuItem class="bg-muted">
                <Icon
                  name="LayoutGrid"
                  class="w-3.5 h-3.5 mr-2 flex-shrink-0 text-muted-foreground"
                />
                <span class="truncate">All Applications</span>
                <Icon name="Check" class="w-3.5 h-3.5 ml-auto text-primary flex-shrink-0" />
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem v-for="b in boardsStore.boards" :key="b.id" @click="switchBoard(b)">
                <span
                  :class="['w-2 h-2 rounded-full mr-2 flex-shrink-0', b.color || 'bg-blue-500']"
                />
                <span class="truncate">{{ b.name }}</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
          <p class="text-xs text-muted-foreground truncate">Jobs across every board</p>
        </div>
      </div>
    </div>

    <Applications />
  </div>
</template>
