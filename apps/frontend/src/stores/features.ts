import { defineStore } from 'pinia';
import dataservice from '@/lib/dataservice';

export type FeatureFlags = Record<string, boolean>

export const useFeatureStore = defineStore('features', {
  state: () => ({
    flags: {} as FeatureFlags,
    loaded: false
  }),
  getters: {
    is:
      (state) =>
        (flag: string): boolean =>
          state.flags[flag] ?? true
  },
  actions: {
    async load() {
      if (this.loaded) return;
      try {
        const res = await dataservice.getFeatures();
        if (res) {
          this.flags = res;
        }
      } catch {
        /* network unavailable — all flags default to true via getter */
      }
      this.loaded = true;
    }
  }
});
