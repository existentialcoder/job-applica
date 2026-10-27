<script setup lang="ts">
import { ref } from 'vue';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import type { EducationEntry } from '@/lib/profile';

const props = defineProps<{ entry: EducationEntry | null }>();
const emit = defineEmits<{ (e: 'save', entry: EducationEntry): void; (e: 'cancel'): void }>();

const institution = ref(props.entry?.institution ?? '');
const degree = ref(props.entry?.degree ?? '');
const field = ref(props.entry?.field ?? '');
// Stored as 'YYYY' or 'YYYY-MM'; the form edits the year.
const start = ref(props.entry?.start?.slice(0, 4) ?? '');
const end = ref(props.entry?.end?.slice(0, 4) ?? '');

function save() {
  emit('save', {
    institution: institution.value.trim(),
    degree: degree.value.trim() || null,
    field: field.value.trim() || null,
    start: String(start.value).trim() || null,
    end: String(end.value).trim() || null
  });
}
</script>

<template>
  <form class="flex flex-col gap-4 rounded-lg border border-border p-4" @submit.prevent="save">
    <div class="grid gap-4 md:grid-cols-2">
      <div class="flex flex-col gap-1.5 md:col-span-2">
        <Label for="edu-institution">School or university</Label>
        <Input id="edu-institution" v-model="institution" placeholder="e.g. Technical University of Munich" required />
      </div>
      <div class="flex flex-col gap-1.5">
        <Label for="edu-degree">Degree</Label>
        <Input id="edu-degree" v-model="degree" placeholder="e.g. B.Sc." />
      </div>
      <div class="flex flex-col gap-1.5">
        <Label for="edu-field">Field of study</Label>
        <Input id="edu-field" v-model="field" placeholder="e.g. Computer Science" />
      </div>
      <div class="flex flex-col gap-1.5">
        <Label for="edu-start">Start year</Label>
        <Input id="edu-start" v-model="start" type="number" placeholder="e.g. 2014" />
      </div>
      <div class="flex flex-col gap-1.5">
        <Label for="edu-end">End year</Label>
        <Input id="edu-end" v-model="end" type="number" placeholder="e.g. 2018" />
      </div>
    </div>
    <div class="flex justify-end gap-2">
      <Button type="button" variant="ghost" @click="emit('cancel')">Cancel</Button>
      <Button type="submit" :disabled="!institution.trim()">Save</Button>
    </div>
  </form>
</template>
