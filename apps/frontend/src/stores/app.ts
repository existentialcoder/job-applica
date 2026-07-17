import { defineStore } from 'pinia';
import dataservice from '@/lib/dataservice';
import { BG_THEMES } from '@job-applica/ui/theme';
export type { BgThemePreview, BgThemeEntry } from '@job-applica/ui/theme';
export { BG_THEMES } from '@job-applica/ui/theme';

export interface BreadcrumbItem {
  label: string
  path?: string
}

interface IAppStore {
  themeMode: 'light' | 'dark' | 'system'
  lightBgTheme: string
  darkBgTheme: string
  sidebarExpanded: boolean
  wrapperWidth: number | string
  wrapperLeftOffset: number | string
  navWidth: number | string
  breadcrumbs: BreadcrumbItem[]
  themeInitialized: boolean
}

const EXPAND = 280;
const SHRINKED = 72;

export const useAppStore = defineStore('app', {
  state: () => <IAppStore>({
    themeMode: 'system',
    lightBgTheme: 'white',
    darkBgTheme: 'noir',
    sidebarExpanded: true,
    wrapperWidth: 0,
    wrapperLeftOffset: 0,
    navWidth: '100%',
    breadcrumbs: [],
    themeInitialized: false,
  }),
  getters: {
    theme: (state) => state.themeMode,
    isDark: (state) => {
      if (state.themeMode === 'system') return window.matchMedia('(prefers-color-scheme: dark)').matches;
      return state.themeMode === 'dark';
    },
  },
  actions: {
    async toggleSidebar() {
      this.sidebarExpanded = !this.sidebarExpanded;
      if (window.innerWidth > 1024) this.initWrapper();
      try {
        await dataservice.updateSettings({ sidebar_expanded: this.sidebarExpanded });
      } catch { /* ignore */ }
    },
    initWrapper() {
      if (window.innerWidth > 1024) {
        this.wrapperWidth = this.sidebarExpanded ? EXPAND : SHRINKED;
        this.wrapperLeftOffset = this.sidebarExpanded ? EXPAND : SHRINKED;
        this.navWidth = `calc(100% - ${this.wrapperWidth}px)`;
      } else {
        this.navWidth = '100%';
        this.sidebarExpanded = false;
        this.wrapperWidth = '100%';
        this.wrapperLeftOffset = '100%';
      }
    },
    applyTheme() {
      const dark = this.isDark;
      document.documentElement.classList.toggle('dark', dark);
      document.documentElement.classList.toggle('light', !dark);
      document.body.classList.toggle('dark', dark);
      document.body.classList.toggle('light', !dark);
      this.applyBgTheme();
    },
    applyBgTheme() {
      const dark = this.isDark;
      const key = dark ? this.darkBgTheme : this.lightBgTheme;
      const palette = dark ? BG_THEMES.dark : BG_THEMES.light;
      const t = palette[key] ?? (dark ? BG_THEMES.dark.noir : BG_THEMES.light.white);

      let el = document.getElementById('__ja_bg__') as HTMLStyleElement | null;
      if (!el) {
        el = document.createElement('style');
        el.id = '__ja_bg__';
        document.head.appendChild(el);
      }
      el.textContent = [
        // Background surface tokens
        `:root { --background: ${t.bg}; --card: ${t.card}; --popover: ${t.card}; }`,
        `.dark { --background: ${t.bg}; --card: ${t.card}; --popover: ${t.card}; }`,
        // Paired accent + foreground — accentFg ensures readable text on filled buttons
        `:root { --primary: ${t.accent}; --primary-foreground: ${t.accentFg}; --ring: ${t.accent}; }`,
        `.dark { --primary: ${t.accent}; --primary-foreground: ${t.accentFg}; --ring: ${t.accent}; }`,
        // body carries the gradient; sidebar is position:fixed so needs its own rule
        `body { background: ${t.body}; background-attachment: fixed; }`,
        `.sidebar { background: ${t.body}; background-attachment: local; background-size: 300% 300%; }`,
      ].join('\n');
    },
    setLightBgTheme(key: string) {
      this.lightBgTheme = key;
      if (!this.isDark) this.applyBgTheme();
      try { dataservice.updateSettings({ light_bg_theme: key }); } catch { /* ignore */ }
    },
    setDarkBgTheme(key: string) {
      this.darkBgTheme = key;
      if (this.isDark) this.applyBgTheme();
      try { dataservice.updateSettings({ dark_bg_theme: key }); } catch { /* ignore */ }
    },
    async setThemeMode(mode: 'light' | 'dark' | 'system') {
      this.themeMode = mode;
      this.applyTheme();
      try {
        await dataservice.updateSettings({ theme: mode });
      } catch { /* ignore */ }
    },
    async toggleTheme() {
      const next = this.isDark ? 'light' : 'dark';
      await this.setThemeMode(next);
    },
    async initTheme() {
      // Guard: set flag synchronously before any await so concurrent calls (e.g. from
      // layouts/app.vue remounting on every navigation) skip setup and just re-apply.
      if (this.themeInitialized) {
        this.applyTheme();
        this.initWrapper();
        return;
      }
      this.themeInitialized = true;

      window.addEventListener('resize', this.initWrapper);
      this.initWrapper();

      window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
        if (this.themeMode === 'system') this.applyTheme();
      });

      try {
        const settings = await dataservice.getSettings();
        const theme = settings.theme as 'light' | 'dark' | 'system' | undefined;
        if (theme === 'light' || theme === 'dark' || theme === 'system') {
          this.themeMode = theme;
        }
        const sidebar = settings.sidebar_expanded;
        if (typeof sidebar === 'boolean') this.sidebarExpanded = sidebar;
        const lightBg = settings.light_bg_theme as string | undefined;
        if (lightBg && lightBg in BG_THEMES.light) this.lightBgTheme = lightBg;
        const darkBg = settings.dark_bg_theme as string | undefined;
        if (darkBg && darkBg in BG_THEMES.dark) this.darkBgTheme = darkBg;
      } catch { /* offline — keep defaults */ }

      this.applyTheme();
      this.initWrapper();
    },
    setBreadcrumbs(items: BreadcrumbItem[]) {
      this.breadcrumbs = items;
    },
    appUnmount() {
      window.removeEventListener('resize', this.initWrapper);
    },
  },
});
