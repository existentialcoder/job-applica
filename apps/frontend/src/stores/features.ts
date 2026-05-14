import { defineStore } from 'pinia';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

// Flags are owned by the backend — no need to mirror them here.
// Unknown flags default to true (fail open) so new flags never hide things unexpectedly.
export type FeatureFlags = Record<string, boolean>;

export const useFeatureStore = defineStore('features', {
  state: () => ({
    flags: {} as FeatureFlags,
    loaded: false,
  }),
  getters: {
    is: (state) => (flag: string): boolean => state.flags[flag] ?? true,
  },
  actions: {
    async load() {
      if (this.loaded) return;
      try {
        const res = await fetch(`${API_BASE}/features`);
        if (res.ok) this.flags = await res.json();
      } catch { /* network unavailable — all flags default to true via getter */ }
      this.loaded = true;
    },
  },
});
