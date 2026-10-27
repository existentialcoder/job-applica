<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import CityInput from '@/components/onboarding/CityInput.vue';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Combobox } from '@/components/ui/combobox';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Select, SelectContent, SelectGroup, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Toggle } from '@/components/ui/toggle';
import {
  COUNTRY_OPTIONS,
  CURRENCY_OPTIONS,
  ONBOARDING_STEP,
  POSITION_OPTIONS,
  WORK_MODEL_OPTIONS
} from '@/lib/constants';
import type { JobPreferences } from '@/lib/profile';
import { useOnboardingStore } from '@/stores/onboarding';
import { useProfileStore } from '@/stores/profile';

const JOB_TYPES = ['Full-time', 'Contract', 'Part-time'];
const NOTICE = [
  { days: 0, label: 'Available now' },
  { days: 14, label: '2 weeks' },
  { days: 30, label: '1 month' },
  { days: 60, label: '2 months' },
  { days: 90, label: '3 months' }
];
const YES_NO = [
  { key: 'open_to_relocation', label: 'Open to relocation' },
  { key: 'needs_visa_sponsorship', label: 'I need visa sponsorship' }
] as const;
const COUNTRIES = COUNTRY_OPTIONS.map((c) => ({ label: c, value: c }));
const CURRENCIES = CURRENCY_OPTIONS.map((c) => ({ label: `${c.code} · ${c.name}`, value: c.code }));

const profileStore = useProfileStore();
const onboardingStore = useOnboardingStore();
const prefs = ref<JobPreferences>({
  target_titles: [],
  locations: [],
  work_models: [],
  seniority: [],
  job_types: [],
  salary_min: null,
  salary_currency: null,
  salary_period: null,
  notice_period_days: null,
  open_to_relocation: false,
  needs_visa_sponsorship: false
});
const newTitle = ref('');
// Titles the user has held, latest first, offered as one-click target titles.
const pastTitles = ref<string[]>([]);
const suggestions = computed(() => pastTitles.value.filter((t) => !prefs.value.target_titles.includes(t)));
const newCity = ref('');
const newCountry = ref('');
const salary = ref('');
const currency = ref('');
const currencyPicked = ref(false);
const notice = ref('');
const locating = ref(false);
const locateFailed = ref(false);
const loading = ref(true);
const saving = ref(false);
const error = ref('');
const salaryAmount = computed(() => Number(salary.value.replace(/[^\d]/g, '')) || null);
const currencyMissing = computed(() => !!salaryAmount.value && !currency.value);
const salaryMissing = computed(() => currencyPicked.value && !salaryAmount.value);
const complete = computed(
  () =>
    prefs.value.target_titles.length > 0 &&
    prefs.value.locations.length > 0 &&
    !currencyMissing.value &&
    !salaryMissing.value &&
    notice.value !== ''
);

function pickCurrency(value: string) {
  currency.value = value;
  currencyPicked.value = !!value;
}

onMounted(async () => {
  const [saved, profile] = await Promise.all([
    profileStore.fetchPreferences(),
    profileStore.fetchProfile()
  ]);
  if (profile) {
    const titles = [profile.current_title, ...profile.experience.map((e) => e.title)];
    pastTitles.value = [...new Set(titles.map((t) => t?.trim()).filter((t): t is string => !!t))];
  }
  if (saved) {
    prefs.value = saved;
    salary.value = saved.salary_min === null ? '' : String(saved.salary_min);
    currency.value = saved.salary_currency ?? '';
    currencyPicked.value = !!saved.salary_currency;
    notice.value = saved.notice_period_days === null ? '' : String(saved.notice_period_days);
  }
  if (notice.value === '') notice.value = '30';
  if (!prefs.value.target_titles.length && pastTitles.value.length) prefs.value.target_titles = [pastTitles.value[0]];
  // Same pick as the backend's current_role(): the ongoing role, else the one that started last.
  const experience = profile?.experience ?? [];
  const ongoing = experience.filter((e) => !e.end);
  const role = [...(ongoing.length ? ongoing : experience)].sort((a, b) => (b.start ?? '').localeCompare(a.start ?? ''))[0];
  if (role) {
    if (!prefs.value.work_models.length && role.work_model) prefs.value.work_models = [role.work_model];
    if (!prefs.value.seniority.length && role.seniority) prefs.value.seniority = [role.seniority];
    if (!prefs.value.job_types.length && role.job_type) prefs.value.job_types = [role.job_type];
  }
  const { city, country } = profile?.contacts ?? {};
  if (!prefs.value.locations.length && (city || country)) {
    prefs.value.locations = [{ city: city ?? null, country: country ?? null }];
  }
  loading.value = false;
  if (!prefs.value.locations.length || !currency.value) useMyLocation(false);
});

function toggle(list: string[], value: string) {
  const i = list.indexOf(value);
  if (i === -1) list.push(value);
  else list.splice(i, 1);
}

function addTitle() {
  const title = newTitle.value.trim();
  if (title && !prefs.value.target_titles.includes(title)) prefs.value.target_titles.push(title);
  newTitle.value = '';
}

/** Add a location unless the same one is already listed. */
function addPlace(here: { city: string | null; country: string | null }) {
  const key = place(here).toLowerCase();
  if (!prefs.value.locations.some((l) => place(l).toLowerCase() === key)) prefs.value.locations.push(here);
}

function addLocation() {
  if (!newCity.value.trim() && !newCountry.value) return;
  addPlace({ city: newCity.value.trim() || null, country: newCountry.value || null });
  newCity.value = '';
  newCountry.value = '';
}

function browserCoords(): Promise<{ lat: number; lng: number } | undefined> {
  return new Promise((resolve) => {
    if (!navigator.geolocation) return resolve(undefined);
    navigator.geolocation.getCurrentPosition(
      (pos) => resolve({ lat: pos.coords.latitude, lng: pos.coords.longitude }),
      () => resolve(undefined),
      { timeout: 10_000 }
    );
  });
}

// The country comes from the IP (Cloudflare). In local dev, where there is no Cloudflare, the browser's
// coordinates stand in (the backend only accepts them there), so only ask for them when the user clicks:
// a permission prompt on page load would be out of nowhere.
async function useMyLocation(asked = true) {
  locating.value = true;
  locateFailed.value = false;
  const found = await profileStore.detectLocale(asked && import.meta.env.DEV ? await browserCoords() : undefined);
  locating.value = false;
  if (!found?.country) {
    locateFailed.value = asked;
    return;
  }
  if (asked || !prefs.value.locations.length) addPlace({ city: found.city, country: found.country });
  if (!currency.value && found.currency) currency.value = found.currency;
}

const place = (l: { city: string | null; country: string | null }) => [l.city, l.country].filter(Boolean).join(', ');

async function finish() {
  saving.value = true;
  error.value = '';
  try {
    await profileStore.savePreferences({
      ...prefs.value,
      salary_min: salaryAmount.value,
      salary_currency: salaryAmount.value ? currency.value : null,
      salary_period: salaryAmount.value ? 'year' : null,
      notice_period_days: Number(notice.value)
    });
    await onboardingStore.finish();
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to save preferences';
  } finally {
    saving.value = false;
  }
}
</script>

<template>
  <div class="flex flex-col gap-5">
    <div>
      <h1 class="text-2xl font-bold tracking-tight">{{ ONBOARDING_STEP.preferences.title }}</h1>
      <p class="mt-1 text-sm text-muted-foreground">{{ ONBOARDING_STEP.preferences.hint }}</p>
    </div>

    <template v-if="!loading">
      <section class="card" aria-labelledby="titles">
        <h2 id="titles" class="section-title">Target job titles <span class="text-destructive">*</span></h2>
        <ul v-if="prefs.target_titles.length" class="flex flex-wrap gap-2">
          <li v-for="(t, i) in prefs.target_titles" :key="t">
            <Badge variant="secondary" class="gap-1.5">
              {{ t }}
              <button type="button" class="flex" :aria-label="`Remove ${t}`" @click="prefs.target_titles.splice(i, 1)">
                <Icon name="X" :size="12" :stroke-width="2" />
              </button>
            </Badge>
          </li>
        </ul>
        <div v-if="suggestions.length" class="flex flex-wrap items-center gap-2">
          <span class="hint">From your experience:</span>
          <Button
            v-for="t in suggestions"
            :key="t"
            variant="outline"
            size="sm"
            class="h-7 rounded-full px-2.5 text-xs font-normal"
            :aria-label="`Add ${t}`"
            @click="prefs.target_titles.push(t)"
          >
            <Icon name="Plus" :size="12" :stroke-width="2" default-class="mr-1" />{{ t }}
          </Button>
        </div>
        <form class="flex gap-2 md:w-2/3" @submit.prevent="addTitle">
          <Input v-model="newTitle" placeholder="e.g. Staff Engineer" aria-label="Add a job title" />
          <Button type="submit" variant="outline" :disabled="!newTitle.trim()">Add</Button>
        </form>
      </section>

      <section class="card" aria-labelledby="how">
        <h2 id="how" class="section-title">How and where you work</h2>
        <div role="group" aria-labelledby="locations" class="group gap-2.5">
          <div class="flex flex-wrap items-center justify-between gap-2">
            <span id="locations" class="label mb-0">Locations <span class="text-destructive">*</span></span>
            <Button variant="ghost" size="sm" class="text-primary" :disabled="locating" @click="useMyLocation()">
              <Icon name="LocateFixed" :size="16" :stroke-width="2" default-class="mr-1.5" />
              {{ locating ? 'Finding you…' : 'Use my current location' }}
            </Button>
          </div>
          <p v-if="locateFailed" role="status" class="hint">We couldn't find your location. Add it below.</p>
          <ul v-if="prefs.locations.length" class="flex flex-wrap gap-2">
            <li v-for="(l, i) in prefs.locations" :key="i">
              <Badge variant="secondary" class="gap-1.5">
                {{ place(l) }}
                <button type="button" class="flex" :aria-label="`Remove ${place(l)}`" @click="prefs.locations.splice(i, 1)">
                  <Icon name="X" :size="12" :stroke-width="2" />
                </button>
              </Badge>
            </li>
          </ul>
          <form class="grid gap-2 md:grid-cols-[minmax(0,1fr)_minmax(0,1fr)_auto]" @submit.prevent="addLocation">
            <CityInput
              v-model="newCity"
              placeholder="City, e.g. Berlin"
              aria-label="City"
              @select="newCountry = $event.country ?? newCountry"
            />
            <Combobox v-model="newCountry" :options="COUNTRIES" placeholder="Select a country" class="h-10" />
            <Button type="submit" variant="outline" :disabled="!newCity.trim() && !newCountry">Add</Button>
          </form>
        </div>
        <fieldset class="group">
          <legend class="label">Work model</legend>
          <div class="flex flex-wrap gap-2">
            <Toggle
              v-for="m in WORK_MODEL_OPTIONS"
              :key="m"
              variant="outline"
              class="data-[state=on]:border-primary data-[state=on]:bg-primary/15 data-[state=on]:text-primary"
              :pressed="prefs.work_models.includes(m)"
              @update:pressed="toggle(prefs.work_models, m)"
            >
              {{ m }}
            </Toggle>
          </div>
        </fieldset>
        <fieldset class="group">
          <legend class="label">Seniority</legend>
          <div class="flex flex-wrap gap-2">
            <Toggle
              v-for="s in POSITION_OPTIONS"
              :key="s"
              variant="outline"
              class="data-[state=on]:border-primary data-[state=on]:bg-primary/15 data-[state=on]:text-primary"
              :pressed="prefs.seniority.includes(s)"
              @update:pressed="toggle(prefs.seniority, s)"
            >
              {{ s }}
            </Toggle>
          </div>
        </fieldset>
        <fieldset class="group">
          <legend class="label">Job type</legend>
          <div class="flex flex-wrap gap-2">
            <Toggle
              v-for="t in JOB_TYPES"
              :key="t"
              variant="outline"
              class="data-[state=on]:border-primary data-[state=on]:bg-primary/15 data-[state=on]:text-primary"
              :pressed="prefs.job_types.includes(t)"
              @update:pressed="toggle(prefs.job_types, t)"
            >
              {{ t }}
            </Toggle>
          </div>
        </fieldset>
      </section>

      <section class="card" aria-labelledby="salary">
        <h2 id="salary" class="section-title">Salary and notice period</h2>
        <div class="grid gap-4 md:grid-cols-3">
          <div class="field">
            <Label for="pref-salary">
              Minimum yearly salary <span v-if="currencyPicked" class="text-destructive">*</span>
            </Label>
            <Input
              id="pref-salary"
              v-model="salary"
              inputmode="numeric"
              placeholder="e.g. 65000"
              :aria-invalid="salaryMissing"
              :aria-describedby="salaryMissing ? 'salary-hint' : undefined"
            />
            <p v-if="salaryMissing" id="salary-hint" class="text-[13px] text-destructive">
              Add the salary for this currency
            </p>
          </div>
          <div class="field">
            <Label>Currency <span v-if="salaryAmount" class="text-destructive">*</span></Label>
            <Combobox
              :model-value="currency"
              :options="CURRENCIES"
              placeholder="Select a currency"
              clearable
              class="h-10"
              :class="{ 'border-destructive': currencyMissing }"
              @update:model-value="pickCurrency"
            />
            <p v-if="currencyMissing" class="text-[13px] text-destructive">Choose the currency for your salary</p>
          </div>
          <div class="field">
            <Label>Notice period <span class="text-destructive">*</span></Label>
            <Select v-model="notice">
              <SelectTrigger>
                <SelectValue placeholder="Select a notice period" />
              </SelectTrigger>
              <SelectContent>
                <SelectGroup>
                  <SelectItem v-for="n in NOTICE" :key="n.days" :value="String(n.days)">{{ n.label }}</SelectItem>
                </SelectGroup>
              </SelectContent>
            </Select>
          </div>
        </div>
        <fieldset v-for="q in YES_NO" :key="q.key" class="choice-row">
          <legend class="sr-only">{{ q.label }}</legend>
          <span class="text-sm font-medium" aria-hidden="true">{{ q.label }}</span>
          <RadioGroup
            :model-value="prefs[q.key] ? 'yes' : 'no'"
            orientation="horizontal"
            class="flex gap-5"
            @update:model-value="prefs[q.key] = $event === 'yes'"
          >
            <div v-for="o in ['yes', 'no']" :key="o" class="flex items-center gap-2">
              <RadioGroupItem :id="`${q.key}-${o}`" :value="o" />
              <Label :for="`${q.key}-${o}`" class="font-normal">{{ o === 'yes' ? 'Yes' : 'No' }}</Label>
            </div>
          </RadioGroup>
        </fieldset>
      </section>
    </template>

    <Teleport to="#onboarding-actions">
      <p v-if="error" role="alert" class="text-sm text-destructive">{{ error }}</p>
      <Button :disabled="loading || saving || !complete" @click="finish">
        {{ saving ? 'Saving…' : 'Finish setup' }}
        <Icon name="ArrowRight" :size="16" :stroke-width="2" default-class="ml-2" />
      </Button>
    </Teleport>
  </div>
</template>

<style scoped>
.card {
  @apply rounded-xl border border-border bg-card p-6 flex flex-col gap-4;
}

.section-title {
  @apply text-sm font-semibold;
}

.hint {
  @apply text-[13px] text-muted-foreground;
}

.label {
  @apply text-sm font-medium leading-none mb-2.5;
}

.group {
  @apply flex flex-col;
}

.field {
  @apply flex flex-col gap-1.5;
}

.choice-row {
  @apply flex flex-wrap items-center justify-between gap-x-4 gap-y-2 pt-4 border-t border-border;
}
</style>
