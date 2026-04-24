import { defineStore } from 'pinia';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

interface IAppStore {
  themeMode: 'light' | 'dark'
  sidebarExpand: boolean
  wrapperWidth: number | string
  wrapperLeftOffset: number | string
  navWidth: number | string
}

const LIGHT = 'light';
const DARK = 'dark';
const EXPAND = 280;
const SHRINKED = 72;

function authHeader(): Record<string, string> {
  const token = localStorage.getItem('access_token');
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export const useAppStore = defineStore('app', {
  state: () => <IAppStore>({
    themeMode: LIGHT,
    sidebarExpand: true,
    wrapperWidth: 0,
    wrapperLeftOffset: 0,
    navWidth: '100%'
  }),
  getters: {
    theme: (state) => state.themeMode,
    isDark: (state) => state.themeMode === DARK,
    sidebarExpanded: (state) => state.sidebarExpand,
  },
  actions: {
    toggleSidebar() {
      this.sidebarExpand = !this.sidebarExpand;
      if (window.innerWidth > 1024) {
        this.initWrapper();
      }
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
      const token = localStorage.getItem('access_token');
      if (token) {
        try {
          const res = await fetch(`${API_BASE}/auth/settings`, {
            headers: { ...authHeader() },
          });
          if (res.ok) {
            const data = await res.json();
            const theme = data.settings?.theme as 'light' | 'dark' | undefined;
            if (theme === LIGHT || theme === DARK) {
              this.themeMode = theme;
              this.applyTheme();
              return;
            }
          }
        } catch { /* network unavailable — fall through to localStorage */ }
      }

      const cached = localStorage.getItem('themeMode');
      if (cached === LIGHT || cached === DARK) {
        this.themeMode = cached;
      }
      this.applyTheme();
    },
    async toggleTheme() {
      this.themeMode = this.themeMode === LIGHT ? DARK : LIGHT;
      this.applyTheme();

      // Persist to API (best-effort) and localStorage as fallback
      localStorage.setItem('themeMode', this.themeMode);
      try {
        await fetch(`${API_BASE}/auth/settings`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json', ...authHeader() },
          body: JSON.stringify({ settings: { theme: this.themeMode } }),
        });
      } catch { /* ignore network errors */ }
    },
    appUnmount() {
      window.removeEventListener('resize', this.initWrapper);
    },
  },
});
