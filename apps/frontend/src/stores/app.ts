import { defineStore } from 'pinia';
import { useSettingsStore } from '@/stores/settings';

export interface BreadcrumbItem {
  label: string
  path?: string
}

interface IAppStore {
  wrapperWidth: number | string
  wrapperLeftOffset: number | string
  navWidth: number | string
  breadcrumbs: BreadcrumbItem[]
}

const EXPAND = 280;
const SHRINKED = 72;

export const useAppStore = defineStore('app', {
  state: () =>
    <IAppStore>{
      wrapperWidth: 0,
      wrapperLeftOffset: 0,
      navWidth: '100%',
      breadcrumbs: []
    },
  actions: {
    initWrapper() {
      const settingsStore = useSettingsStore();
      if (window.innerWidth > 1024) {
        this.wrapperWidth = settingsStore.settings.sidebarExpanded ? EXPAND : SHRINKED;
        this.wrapperLeftOffset = settingsStore.settings.sidebarExpanded ? EXPAND : SHRINKED;
        this.navWidth = `calc(100% - ${this.wrapperWidth}px)`;
      } else {
        this.navWidth = '100%';
        settingsStore.settings.sidebarExpanded = false;
        this.wrapperWidth = '100%';
        this.wrapperLeftOffset = '100%';
      }
    },
    setBreadcrumbs(items: BreadcrumbItem[]) {
      this.breadcrumbs = items;
    },
    appUnmount() {
      window.removeEventListener('resize', this.initWrapper);
    }
  }
});
