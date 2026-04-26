<script setup lang="ts">
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import Breadcrumb from '@/components/ui/Breadcrumb.vue';
import { LogOut, User, Bell, Sun, MoonStar, Menu } from 'lucide-vue-next';
import { Button } from '@/components/ui/button';
import { useAppStore } from '@/stores/app';
import { useAuthStore } from '@/stores/auth';

const store = useAppStore();
const authStore = useAuthStore();
const router = useRouter();

const initials = computed(() => {
  const u = authStore.user;
  if (!u) return '?';
  return `${u.first_name?.[0] ?? ''}${u.last_name?.[0] ?? ''}`.toUpperCase();
});

async function handleLogout() {
  await authStore.logout();
}
</script>

<template>
  <nav
    class="flex items-center justify-between h-[64px] border-b-[1px] px-4 fixed z-40 top-0 bg-background/80 backdrop-blur-lg border-b border-border"
    :style="{ width: store.navWidth }"
  >
    <div class="min-w-0 max-w-xs hidden lg:block">
      <Breadcrumb />
    </div>
    <div class="flex-1 hidden lg:block" />

    <Button
      variant="outline"
      class="p-[6px] w-8 h-8 transition-all duration-200 block lg:hidden"
      :class="store.sidebarExpanded ? 'bg-transparent' : 'dark:bg-white'"
      @click="store.toggleSidebar()"
    >
      <Menu class="transition-all duration-500 text-black" />
    </Button>

    <div class="flex items-center">
      <Button variant="outline" class="border-0 p-[6px] w-8 h-8">
        <Bell />
      </Button>
      <Button variant="outline" class="border-0 p-[6px] ml-2 w-8 h-8" @click="store.toggleTheme()">
        <Sun v-if="store.isDark" />
        <MoonStar v-else />
      </Button>
      <div class="border-x-[1px] border-gray-300 h-[24px] w-[1px] mx-2" />

      <DropdownMenu>
        <DropdownMenuTrigger as-child>
          <Button variant="outline" class="border-0 flex items-center max-w-[220px] w-full justify-start gap-2">
            <Avatar class="h-8 w-8 flex-shrink-0">
              <AvatarImage v-if="authStore.user?.avatar_url" :src="authStore.user.avatar_url" :alt="authStore.displayName" />
              <AvatarFallback class="text-xs font-semibold">{{ initials }}</AvatarFallback>
            </Avatar>
            <span class="hidden md:flex flex-col items-start min-w-0">
              <p class="text-sm font-medium leading-tight truncate max-w-[140px]">{{ authStore.displayName }}</p>
              <small class="text-xs text-muted-foreground font-light truncate max-w-[140px]">
                {{ authStore.user?.email ?? authStore.user?.user_name }}
              </small>
            </span>
          </Button>
        </DropdownMenuTrigger>

        <DropdownMenuContent class="w-56 relative mr-4">
          <DropdownMenuLabel class="font-normal">
            <div class="flex flex-col gap-0.5">
              <p class="font-semibold">{{ authStore.displayName }}</p>
              <p class="text-xs text-muted-foreground truncate">{{ authStore.user?.email ?? authStore.user?.user_name }}</p>
            </div>
          </DropdownMenuLabel>
          <DropdownMenuSeparator />
          <DropdownMenuItem>
            <User class="mr-2 h-4 w-4" />
            <span>Profile</span>
          </DropdownMenuItem>
          <DropdownMenuSeparator />
          <DropdownMenuItem class="text-destructive focus:text-destructive cursor-pointer" @click="handleLogout">
            <LogOut class="mr-2 h-4 w-4" />
            <span>Log out</span>
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  </nav>
</template>
