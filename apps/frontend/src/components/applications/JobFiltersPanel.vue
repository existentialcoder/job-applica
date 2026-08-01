<script setup lang="ts">
import { reactive, watch } from 'vue'
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetFooter } from '@/components/ui/sheet'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { MultiSelect } from '@/components/ui/multi-select'
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue
} from '@/components/ui/select'
import DatePickerInput from './DatePickerInput.vue'
import { POSITION_OPTIONS, WORK_MODEL_OPTIONS, COUNTRY_OPTIONS } from '@/lib/constants'
import { emptyJobFilters, resolvePresetRange, type JobFiltersFormValues } from '@/lib/jobFilters'
import dataservice from '@/lib/dataservice'
import { toast } from '@/lib/toast'

const props = defineProps<{
  open: boolean
  modelValue: JobFiltersFormValues
  statusOptions: string[]
  boardOptions?: { label: string; value: string }[]
}>()

const emit = defineEmits<{
  (e: 'update:open', val: boolean): void
  (e: 'update:modelValue', val: JobFiltersFormValues): void
}>()

const DATE_PRESET_OPTIONS = [
  { value: '7d', label: 'Last 1 week' },
  { value: '14d', label: 'Last 2 weeks' },
  { value: '30d', label: 'Last 1 month' },
  { value: 'custom', label: 'Custom range' }
]

// Local draft so edits only apply when "Apply filters" is clicked, not on every keystroke.
const draft = reactive<JobFiltersFormValues>({ ...props.modelValue })

watch(
  () => props.open,
  (open) => {
    if (open) Object.assign(draft, props.modelValue)
  }
)

function statusMultiOptions() {
  return props.statusOptions.map((s) => ({ label: s, value: s }))
}

const WORK_MODEL_MULTI_OPTIONS = WORK_MODEL_OPTIONS.map((w) => ({ label: w, value: w }))
const POSITION_MULTI_OPTIONS = POSITION_OPTIONS.map((p) => ({ label: p, value: p }))
const COUNTRY_MULTI_OPTIONS = COUNTRY_OPTIONS.map((c) => ({ label: c, value: c }))

function onAppliedPresetChange(preset: string) {
  draft.appliedPreset = preset as JobFiltersFormValues['appliedPreset']
  const range = resolvePresetRange(draft.appliedPreset)
  if (range) {
    draft.appliedFrom = range.from
    draft.appliedTo = range.to
  }
}

function onCreatedPresetChange(preset: string) {
  draft.createdPreset = preset as JobFiltersFormValues['createdPreset']
  const range = resolvePresetRange(draft.createdPreset)
  if (range) {
    draft.createdFrom = range.from
    draft.createdTo = range.to
  }
}

function apply() {
  emit('update:modelValue', { ...draft })
  emit('update:open', false)
}

function clear() {
  Object.assign(draft, emptyJobFilters())
  emit('update:modelValue', { ...draft })
  emit('update:open', false)
}

async function saveAsDefault() {
  try {
    await dataservice.updateSettings({ saved_job_filters: { ...draft } })
    toast.success('Saved as your default filter')
  } catch {
    toast.error('Failed to save filter')
  }
}

async function clearSavedDefault() {
  try {
    await dataservice.updateSettings({ saved_job_filters: null })
    toast.success('Saved default filter cleared')
  } catch {
    toast.error('Failed to clear saved filter')
  }
}
</script>

<template>
  <Sheet :open="open" @update:open="$emit('update:open', $event)">
    <SheetContent side="right" class="w-[520px] sm:w-[620px] flex flex-col">
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
            <Input v-model="draft.location" placeholder="City…" />
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
          <Input v-model="draft.company" placeholder="Company name…" />
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
          <div v-if="draft.appliedPreset === 'custom'" class="flex items-center gap-2 mt-1">
            <DatePickerInput v-model="draft.appliedFrom" placeholder="From" class="flex-1" />
            <span class="text-muted-foreground text-xs flex-shrink-0">to</span>
            <DatePickerInput v-model="draft.appliedTo" placeholder="To" class="flex-1" />
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
          <div v-if="draft.createdPreset === 'custom'" class="flex items-center gap-2 mt-1">
            <DatePickerInput v-model="draft.createdFrom" placeholder="From" class="flex-1" />
            <span class="text-muted-foreground text-xs flex-shrink-0">to</span>
            <DatePickerInput v-model="draft.createdTo" placeholder="To" class="flex-1" />
          </div>
        </div>

        <div class="flex flex-col gap-1.5">
          <Label>ATS score range</Label>
          <div class="flex items-center gap-2">
            <Input
              v-model="draft.atsScoreMin"
              type="number"
              min="0"
              max="100"
              placeholder="Min"
              class="flex-1"
            />
            <span class="text-muted-foreground text-xs flex-shrink-0">to</span>
            <Input
              v-model="draft.atsScoreMax"
              type="number"
              min="0"
              max="100"
              placeholder="Max"
              class="flex-1"
            />
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
