import { defineStore } from 'pinia';
import { ref } from 'vue';
import dataservice from '@/lib/dataservice';
import type { ContactDetails, JobPreferences, Profile, ProfileFields } from '@/lib/profile';

export const useProfileStore = defineStore('profile', () => {
  const profile = ref<Profile | null>(null);
  const preferences = ref<JobPreferences | null>(null);

  // Always re-read: the profile is rebuilt in the background after a CV upload or replace.
  async function fetchProfile(): Promise<Profile | null> {
    profile.value = await dataservice.getProfile().catch(() => null);
    return profile.value;
  }

  async function saveProfile(update: ProfileFields & { contacts: ContactDetails; confirm: boolean }) {
    profile.value = await dataservice.saveProfile(update);
    return profile.value;
  }

  async function fetchPreferences(): Promise<JobPreferences | null> {
    preferences.value = await dataservice.getPreferences().catch(() => null);
    return preferences.value;
  }

  async function savePreferences(prefs: JobPreferences) {
    preferences.value = await dataservice.savePreferences(prefs);
    return preferences.value;
  }

  /** Country, city and currency for "Use my current location"; nulls when nothing was found. */
  async function detectLocale(coords?: { lat: number; lng: number }) {
    return dataservice.detectLocale(coords).catch(() => null);
  }

  async function searchCities(q: string) {
    return dataservice.searchCities(q).catch(() => []);
  }

  return { profile, preferences, fetchProfile, saveProfile, fetchPreferences, savePreferences, detectLocale, searchCities };
});
