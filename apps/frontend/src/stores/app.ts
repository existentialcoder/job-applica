import { defineStore } from 'pinia';
import dataservice from '@/lib/dataservice';

export interface BreadcrumbItem {
  label: string
  path?: string
}

interface IAppStore {
  themeMode: 'light' | 'dark'
  sidebarExpand: boolean
  wrapperWidth: number | string
  wrapperLeftOffset: number | string
  navWidth: number | string
  breadcrumbs: BreadcrumbItem[]
}

const LIGHT = 'light';
const DARK = 'dark';
const EXPAND = 280;
const SHRINKED = 72;


export const useAppStore = defineStore('app', {
  state: () => <IAppStore>({
    themeMode: LIGHT,
    sidebarExpand: true,
    wrapperWidth: 0,
    wrapperLeftOffset: 0,
    navWidth: '100%',
    breadcrumbs: [],
  }),
  getters: {
    theme: (state) => state.themeMode,
    isDark: (state) => state.themeMode === DARK,
    sidebarExpanded: (state) => state.sidebarExpand,
  },
  actions: {
    async toggleSidebar() {
      this.sidebarExpand = !this.sidebarExpand;
      if (window.innerWidth > 1024) {
        this.initWrapper();
      }
      try {
        await dataservice.updateSettings({ sidebar_expanded: this.sidebarExpand });
      } catch { /* ignore network errors */ }
    },
    initWrapper() {
      if (window.innerWidth > 1024) {
        if (this.sidebarExpand) {
          this.wrapperWidth = EXPAND;
          this.wrapperLeftOffset = EXPAND;
        } else {
          this.wrapperWidth = SHRINKED;
          this.wrapperLeftOffset = SHRINKED;
        }
        this.navWidth = `calc(100% - ${this.wrapperWidth}px)`
      } else {
        this.navWidth = '100%';
        this.sidebarExpand = false;
        this.wrapperWidth = '100%';
        this.wrapperLeftOffset = '100%';
      }
    },
    applyTheme() {
      document.documentElement.classList.remove(LIGHT, DARK);
      document.body.classList.remove(LIGHT, DARK);
      document.documentElement.classList.add(this.themeMode);
      document.body.classList.add(this.themeMode);
    },
    async initTheme() {
      window.addEventListener('resize', this.initWrapper);
      this.initWrapper();

      // Try to load from API first; fall back to localStorage
      try {
        const settings = await dataservice.getSettings();
        const theme = settings.theme as 'light' | 'dark' | undefined;
        if (theme === LIGHT || theme === DARK) {
          this.themeMode = theme;
        }
        const sidebar = settings.sidebar_expanded;
        if (typeof sidebar === 'boolean') {
          this.sidebarExpand = sidebar;
        }
        this.applyTheme();
        this.initWrapper();
        return;
      } catch { /* network unavailable — fall through to localStorage */ }

      const cached = localStorage.getItem('themeMode');
      if (cached === LIGHT || cached === DARK) {
        this.themeMode = cached;
      }
      this.applyTheme();
    },
    async toggleTheme() {
      this.themeMode = this.themeMode === LIGHT ? DARK : LIGHT;
      this.applyTheme();

      localStorage.setItem('themeMode', this.themeMode);
      try {
        await dataservice.updateSettings({ theme: this.themeMode });
      } catch { /* ignore network errors */ }
    },
    setBreadcrumbs(items: BreadcrumbItem[]) {
      this.breadcrumbs = items;
    },
    appUnmount() {
      window.removeEventListener('resize', this.initWrapper);
    },
  },
});
