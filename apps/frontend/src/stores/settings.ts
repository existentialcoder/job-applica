import { BG_THEMES } from '@job-applica/ui/theme';
import { defineStore } from 'pinia';
import { ref, computed, watch } from 'vue';
import dataservice from '@/lib/dataservice';
import { toast } from '@/lib/toast';
import { useAppStore } from '@/stores/app';
export type { BgThemePreview, BgThemeEntry } from '@job-applica/ui/theme';
export { BG_THEMES } from '@job-applica/ui/theme';

interface Settings {
  themeMode: 'light' | 'dark' | 'system' | null
  lightBgTheme: string | null
  darkBgTheme: string | null
  sidebarExpanded: boolean | null
  viewMode: 'list' | 'board' | null
  perPage: number | null
  hiddenWidgets: string[] | null
  savedJobFilters: Record<string, unknown> | null
}

type SettingsPatch = Partial<Settings>

const WIRE_KEYS: Record<keyof Settings, string> = {
  themeMode: 'theme',
  lightBgTheme: 'light_bg_theme',
  darkBgTheme: 'dark_bg_theme',
  sidebarExpanded: 'sidebar_expanded',
  viewMode: 'view_mode',
  perPage: 'per_page',
  hiddenWidgets: 'hidden_widgets',
  savedJobFilters: 'saved_job_filters'
};

const LOCAL_KEYS: Record<string, keyof Settings> = Object.fromEntries(
  (Object.entries(WIRE_KEYS) as [keyof Settings, string][]).map(([local, wire]) => [wire, local])
);

export const useSettingsStore = defineStore('settings', () => {
  const settings = ref<Settings>({
    themeMode: null,
    lightBgTheme: null,
    darkBgTheme: null,
    sidebarExpanded: null,
    viewMode: null,
    perPage: null,
    hiddenWidgets: null,
    savedJobFilters: null
  });
  const themeInitialized = ref(false);
  const loaded = ref(false);
  let inFlight: Promise<void> | null = null;

  const isDark = computed(() => {
    if (settings.value.themeMode === 'system' || settings.value.themeMode === null) {
      return window.matchMedia('(prefers-color-scheme: dark)').matches;
    }
    return settings.value.themeMode === 'dark';
  });

  function applyBgTheme() {
    const key = isDark.value ? settings.value.darkBgTheme : settings.value.lightBgTheme;
    if (!key) {
      return;
    }
    const palette = isDark.value ? BG_THEMES.dark : BG_THEMES.light;
    const t = palette[key];
    if (!t) {
      return;
    }

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
      `.sidebar { background: ${t.body}; background-attachment: local; background-size: 300% 300%; }`
    ].join('\n');
  }

  function applyTheme() {
    document.documentElement.classList.toggle('dark', isDark.value);
    document.documentElement.classList.toggle('light', !isDark.value);
    document.body.classList.toggle('dark', isDark.value);
    document.body.classList.toggle('light', !isDark.value);
    applyBgTheme();
  }

  watch(
    () => [settings.value.themeMode, settings.value.lightBgTheme, settings.value.darkBgTheme],
    applyTheme,
    { immediate: true }
  );

  async function updateSettings(patch: SettingsPatch): Promise<boolean> {
    const wirePatch: Record<string, unknown> = {};
    (Object.keys(patch) as (keyof SettingsPatch)[]).forEach((key) => {
      wirePatch[WIRE_KEYS[key]] = patch[key];
    });

    let saved: Record<string, unknown>;
    try {
      ({ settings: saved } = await dataservice.updateSettings(wirePatch));
    } catch {
      toast.error('Failed to save settings');
      return false;
    }

    (Object.keys(saved) as string[]).forEach((wireKey) => {
      const localKey = LOCAL_KEYS[wireKey];
      if (localKey && saved[wireKey] !== undefined) {
        (settings.value as Record<string, unknown>)[localKey] = saved[wireKey];
      }
    });

    if ('sidebarExpanded' in patch && window.innerWidth > 1024) {
      useAppStore().initWrapper();
    }
    return true;
  }

  function toggleSidebar() {
    return updateSettings({ sidebarExpanded: !settings.value.sidebarExpanded });
  }

  function setLightBgTheme(key: string) {
    return updateSettings({ lightBgTheme: key });
  }

  function setDarkBgTheme(key: string) {
    return updateSettings({ darkBgTheme: key });
  }

  function setThemeMode(mode: 'light' | 'dark' | 'system') {
    return updateSettings({ themeMode: mode });
  }

  function setViewMode(mode: 'list' | 'board') {
    return updateSettings({ viewMode: mode });
  }

  function setPerPage(perPage: number) {
    return updateSettings({ perPage });
  }

  function setHiddenWidgets(hiddenWidgets: string[]) {
    return updateSettings({ hiddenWidgets });
  }

  function setSavedJobFilters(savedJobFilters: Record<string, unknown> | null) {
    return updateSettings({ savedJobFilters });
  }

  async function toggleTheme() {
    const next = isDark.value ? 'light' : 'dark';
    return setThemeMode(next);
  }

  async function initTheme() {
    const appStore = useAppStore();
    if (themeInitialized.value) {
      appStore.initWrapper();
      return;
    }
    themeInitialized.value = true;

    window.addEventListener('resize', appStore.initWrapper);
    appStore.initWrapper();

    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
      if (settings.value.themeMode === 'system' || settings.value.themeMode === null) applyTheme();
    });
  }

  async function fetch(force = false) {
    if (loaded.value && !force) {
      return;
    }
    if (inFlight) {
      return inFlight;
    }
    inFlight = (async () => {
      try {
        const fetched = await dataservice.getSettings();
        (Object.keys(fetched) as string[]).forEach((wireKey) => {
          const localKey = LOCAL_KEYS[wireKey];
          if (localKey) {
            (settings.value as Record<string, unknown>)[localKey] = fetched[wireKey];
          }
        });
        loaded.value = true;
      } catch {
        /* offline / unauthenticated — keep current values, retry on the next call */
      } finally {
        inFlight = null;
      }

      useAppStore().initWrapper();
    })();
    return inFlight;
  }

  function reset() {
    settings.value = {
      themeMode: null,
      lightBgTheme: null,
      darkBgTheme: null,
      sidebarExpanded: null,
      viewMode: null,
      perPage: null,
      hiddenWidgets: null,
      savedJobFilters: null
    };
    loaded.value = false;
  }

  return {
    settings,
    themeInitialized,
    loaded,
    isDark,
    fetch,
    updateSettings,
    toggleSidebar,
    applyTheme,
    applyBgTheme,
    setLightBgTheme,
    setDarkBgTheme,
    setThemeMode,
    setViewMode,
    setPerPage,
    setHiddenWidgets,
    setSavedJobFilters,
    toggleTheme,
    initTheme,
    reset
  };
});
