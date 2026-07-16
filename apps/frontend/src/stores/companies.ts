import { defineStore } from 'pinia';
import { ref } from 'vue';
import dataservice from '@/lib/dataservice';

export interface CompanyOption {
  id: number;
  name: string;
  logo_url?: string;
}

export const useCompaniesStore = defineStore('companies', () => {
  const companies = ref<CompanyOption[]>([]);
  const loaded = ref(false);

  async function fetch(force = false) {
    if (loaded.value && !force) return;
    const result = await dataservice.getCompanies();
    companies.value = Array.isArray(result) ? result : [];
    loaded.value = true;
  }

  async function refresh() {
    return fetch(true);
  }

  return { companies, loaded, fetch, refresh };
});
