<script setup lang="ts">
import { reactive, watch, computed } from 'vue';
import { Button } from '@/components/ui/button';
import { DateRangePicker } from '@/components/ui/daterange-picker';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { MultiSelect } from '@/components/ui/multi-select';
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue
} from '@/components/ui/select';
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetFooter } from '@/components/ui/sheet';
import {
  ATS_SCORE_TIERS,
  POSITION_OPTIONS,
  WORK_MODEL_OPTIONS,
  COUNTRY_OPTIONS
} from '@/lib/constants';
import { emptyJobFilters, resolvePresetRange, type JobFiltersFormValues } from '@/lib/jobFilters';
import { toast } from '@/lib/toast';
import { useCompaniesStore } from '@/stores/companies';
import { useSettingsStore } from '@/stores/settings';

const props = defineProps<{
  open: boolean;
  modelValue: JobFiltersFormValues;
  statusOptions: string[];
  boardOptions?: { label: string; value: string }[];
}>();

const companiesStore = useCompaniesStore();
const settingsStore = useSettingsStore();

const emit = defineEmits<{
  (e: 'update:open', val: boolean): void;
  (e: 'update:modelValue', val: JobFiltersFormValues): void;
}>();

const DATE_PRESET_OPTIONS = [
  { value: '7d', label: 'Last 1 week' },
  { value: '14d', label: 'Last 2 weeks' },
  { value: '30d', label: 'Last 1 month' },
  { value: 'custom', label: 'Custom range' }
];

const draft = reactive<JobFiltersFormValues>({ ...props.modelValue });

watch(
  () => props.open,
  (open) => {
    if (open) Object.assign(draft, props.modelValue);
  }
);

function statusMultiOptions() {
  return props.statusOptions.map((s) => ({ label: s, value: s }));
}

const WORK_MODEL_MULTI_OPTIONS = WORK_MODEL_OPTIONS.map((w) => ({ label: w, value: w }));
const POSITION_MULTI_OPTIONS = POSITION_OPTIONS.map((p) => ({ label: p, value: p }));
const COUNTRY_MULTI_OPTIONS = COUNTRY_OPTIONS.map((c) => ({ label: c, value: c }));
const COMPANY_MULTI_OPTIONS = computed(() =>
  companiesStore.companies.map((c) => ({ label: c.name, value: c.name }))
);

function onAppliedPresetChange(preset: string) {
  draft.appliedPreset = preset as JobFiltersFormValues['appliedPreset'];
  const range = resolvePresetRange(draft.appliedPreset);
  if (range) draft.appliedRange = range;
}

function onCreatedPresetChange(preset: string) {
  draft.createdPreset = preset as JobFiltersFormValues['createdPreset'];
  const range = resolvePresetRange(draft.createdPreset);
  if (range) draft.createdRange = range;
}

function toggleAtsTier(tierKey: string) {
  if (draft.atsScoreTier === tierKey) {
    return (draft.atsScoreTier = '');
  }

  draft.atsScoreTier = tierKey;
}

function atsChipClass(tier: (typeof ATS_SCORE_TIERS)[number]) {
  return draft.atsScoreTier === tier.key ? tier.chipActiveClass : '';
}

function apply() {
  emit('update:modelValue', { ...draft });
  emit('update:open', false);
}

function clear() {
  Object.assign(draft, emptyJobFilters());
  emit('update:modelValue', { ...draft });
  emit('update:open', false);
}

async function saveAsDefault() {
  const ok = await settingsStore.setSavedJobFilters({ ...draft });
  if (ok) toast.success('Saved as your default filter');
}

async function clearSavedDefault() {
  const ok = await settingsStore.setSavedJobFilters(null);
  if (ok) toast.success('Saved default filter cleared');
}
</script>

<template>
  <Sheet :open="open" @update:open="$emit('update:open', $event)">
    <SheetContent side="right" class="w-[700px] sm:w-[620px] flex flex-col">
      <SheetHeader>
        <SheetTitle>Filter jobs</SheetTitle>
      </SheetHeader>

      <div class="flex-1 overflow-y-auto flex flex-col gap-4 py-4">
        <div v-if="boardOptions?.length" class="flex flex-col gap-1.5">
          <Label>Board</Label>
          <MultiSelect v-model="draft.boardIds" :options="boardOptions" placeholder="Any board" />
        </div>

        <div class="flex flex-col gap-1.5">
          <Label>Status</Label>
          <MultiSelect
            v-model="draft.status"
            :options="statusMultiOptions()"
            placeholder="Any status"
          />
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div class="flex flex-col gap-1.5">
            <Label>City</Label>
            <Input v-model="draft.city" placeholder="City…" />
          </div>
          <div class="flex flex-col gap-1.5">
            <Label>Country</Label>
            <MultiSelect
              v-model="draft.country"
              :options="COUNTRY_MULTI_OPTIONS"
              placeholder="Any country"
            />
          </div>
        </div>

        <div class="flex flex-col gap-1.5">
          <Label>Company</Label>
          <MultiSelect
            v-model="draft.company"
            :options="COMPANY_MULTI_OPTIONS"
            placeholder="e.g. Acme Corp"
          />
        </div>

        <div class="flex flex-col gap-1.5">
          <Label>Work model</Label>
          <MultiSelect
            v-model="draft.workModel"
            :options="WORK_MODEL_MULTI_OPTIONS"
            placeholder="Any work model"
          />
        </div>

        <div class="flex flex-col gap-1.5">
          <Label>Seniority</Label>
          <MultiSelect
            v-model="draft.position"
            :options="POSITION_MULTI_OPTIONS"
            placeholder="Any seniority"
          />
        </div>

        <div class="flex flex-col gap-1.5">
          <Label>Applied date</Label>
          <Select :model-value="draft.appliedPreset" @update:model-value="onAppliedPresetChange">
            <SelectTrigger><SelectValue placeholder="Any time" /></SelectTrigger>
            <SelectContent>
              <SelectGroup>
                <SelectItem v-for="p in DATE_PRESET_OPTIONS" :key="p.value" :value="p.value">{{
                  p.label
                }}</SelectItem>
              </SelectGroup>
            </SelectContent>
          </Select>
          <div v-if="draft.appliedPreset === 'custom'" class="mt-1">
            <DateRangePicker v-model="draft.appliedRange" placeholder="Pick a date range" />
          </div>
        </div>

        <div class="flex flex-col gap-1.5">
          <Label>Saved date</Label>
          <Select :model-value="draft.createdPreset" @update:model-value="onCreatedPresetChange">
            <SelectTrigger><SelectValue placeholder="Any time" /></SelectTrigger>
            <SelectContent>
              <SelectGroup>
                <SelectItem v-for="p in DATE_PRESET_OPTIONS" :key="p.value" :value="p.value">{{
                  p.label
                }}</SelectItem>
              </SelectGroup>
            </SelectContent>
          </Select>
          <div v-if="draft.createdPreset === 'custom'" class="mt-1">
            <DateRangePicker v-model="draft.createdRange" placeholder="Pick a date range" />
          </div>
        </div>

        <div class="flex flex-col gap-1.5">
          <Label>Match score</Label>
          <div class="flex flex-wrap gap-1.5">
            <Button
              v-for="tier in ATS_SCORE_TIERS"
              :key="tier.key"
              type="button"
              size="sm"
              variant="outline"
              :class="atsChipClass(tier)"
              @click="toggleAtsTier(tier.key)"
            >
              {{ tier.label }} ({{ tier.min }}{{ tier.key === 'excellent' ? '+' : `-${tier.max}` }})
            </Button>
          </div>
        </div>
      </div>

      <SheetFooter class="flex-col gap-2 sm:flex-col">
        <div class="flex justify-between w-full">
          <Button variant="ghost" @click="clear">Clear all</Button>
          <Button @click="apply">Apply filters</Button>
        </div>
        <div class="flex justify-between w-full">
          <Button
            variant="link"
            size="sm"
            class="text-muted-foreground px-0"
            @click="clearSavedDefault"
          >
            Clear saved default
          </Button>
          <Button variant="link" size="sm" class="px-0" @click="saveAsDefault"
            >Save as default</Button
          >
        </div>
      </SheetFooter>
    </SheetContent>
  </Sheet>
</template>
