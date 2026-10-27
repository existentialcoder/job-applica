<script setup lang="ts">
import { ref } from 'vue';
import CompanyCombobox from '@/components/applications/CompanyCombobox.vue';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { MonthPicker } from '@/components/ui/date-picker';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import type { ExperienceEntry } from '@/lib/profile';
import type { CompanyOption } from '@/stores/companies';

const props = defineProps<{ entry: ExperienceEntry | null; companies: CompanyOption[] }>();
const emit = defineEmits<{ (e: 'save', entry: ExperienceEntry): void; (e: 'cancel'): void }>();

const title = ref(props.entry?.title ?? '');
const company = ref(props.entry?.company ?? '');
const start = ref(props.entry?.start ?? '');
const end = ref(props.entry?.end ?? '');
const current = ref(props.entry ? !props.entry.end : false);
const highlights = ref((props.entry?.highlights ?? []).join('\n'));

function save() {
  const name = company.value.trim() || null;
  emit('save', {
    ...props.entry,
    title: title.value.trim(),
    company: name,
    // The extracted website belongs to the extracted company; drop it if the user picks another.
    company_website: name === props.entry?.company ? props.entry?.company_website : null,
    start: start.value || null,
    end: current.value ? null : end.value || null,
    highlights: highlights.value.split('\n').map((h) => h.trim()).filter(Boolean)
  });
}
</script>

<template>
  <form class="flex flex-col gap-4 rounded-lg border border-border p-4" @submit.prevent="save">
    <div class="grid gap-4 md:grid-cols-2">
      <div class="flex flex-col gap-1.5">
        <Label for="exp-title">Job title</Label>
        <Input id="exp-title" v-model="title" placeholder="e.g. Senior Software Engineer" required />
      </div>
      <div class="flex flex-col gap-1.5">
        <Label>Company</Label>
        <CompanyCombobox v-model="company" :companies="companies" placeholder="Select or add a company" class="h-10" />
      </div>
      <div class="flex flex-col gap-1.5">
        <Label>Start</Label>
        <MonthPicker v-model="start" placeholder="Pick a month" />
      </div>
      <div class="flex flex-col gap-1.5">
        <Label>End</Label>
        <MonthPicker v-model="end" :placeholder="current ? 'Present' : 'Pick a month'" :disabled="current" />
      </div>
    </div>
    <div class="flex items-center gap-2">
      <Checkbox id="exp-current" v-model:checked="current" />
      <Label for="exp-current" class="font-normal">I currently work here</Label>
    </div>
    <div class="flex flex-col gap-1.5">
      <Label for="exp-highlights">Highlights</Label>
      <Textarea id="exp-highlights" v-model="highlights" rows="3" placeholder="One achievement per line, e.g. Cut checkout latency by 40%" />
    </div>
    <div class="flex justify-end gap-2">
      <Button type="button" variant="ghost" @click="emit('cancel')">Cancel</Button>
      <Button type="submit" :disabled="!title.trim()">Save</Button>
    </div>
  </form>
</template>
