<script setup lang="ts">
import { ref, watch } from 'vue';
import type { JobData, JobCreatePayload } from '@/lib/types';
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select, SelectContent, SelectGroup, SelectItem, SelectTrigger, SelectValue,
} from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';

const props = defineProps<{
  open: boolean
  editJob?: JobData | null
}>();

const emit = defineEmits<{
  (e: 'update:open', val: boolean): void
  (e: 'save', payload: JobCreatePayload): void
}>();

const STATUS_OPTIONS = ['Saved', 'Applied', 'Phone Screen', 'Interview', 'Technical', 'Offer', 'Rejected', 'Withdrawn'];
const POSITION_OPTIONS = ['Intern', 'Junior', 'Mid', 'Senior', 'Lead', 'Manager'];
const WORK_MODEL_OPTIONS = ['On-site', 'Remote', 'Hybrid'];
const PLATFORM_OPTIONS = ['LinkedIn', 'Indeed', 'Glassdoor', 'Monster', 'ZipRecruiter', 'Jobscan', 'Other'];

const title = ref('');
const companyName = ref('');
const location = ref('');
const status = ref('Saved');
const position = ref('');
const workModel = ref('');
const salaryRange = ref('');
const sourcePlatform = ref('');
const sourceUrl = ref('');
const appliedDate = ref('');
const description = ref('');
const notes = ref('');

function resetForm() {
  title.value = '';
  companyName.value = '';
  location.value = '';
  status.value = 'Saved';
  position.value = '';
  workModel.value = '';
  salaryRange.value = '';
  sourcePlatform.value = '';
  sourceUrl.value = '';
  appliedDate.value = '';
  description.value = '';
  notes.value = '';
}

function populateFromEdit(job: JobData) {
  title.value = job.title || '';
  companyName.value = job.company?.name || '';
  location.value = job.location ? [job.location.city, job.location.state, job.location.country].filter(Boolean).join(', ') : '';
  status.value = job.status || 'Saved';
  position.value = job.position || '';
  workModel.value = job.work_model || '';
  salaryRange.value = job.salary_range || '';
  sourcePlatform.value = job.source_platform || '';
  sourceUrl.value = job.source_url || '';
  appliedDate.value = job.applied_date || '';
  description.value = job.description || '';
  notes.value = job.notes || '';
}

watch(() => props.open, (open) => {
  if (open) {
    if (props.editJob) {
      populateFromEdit(props.editJob);
    } else {
      resetForm();
    }
  }
});

function handleSave() {
  if (!title.value.trim()) return;
  const payload: JobCreatePayload = {
    title: title.value.trim(),
    company_name: companyName.value.trim() || undefined,
    location: location.value.trim() || undefined,
    status: status.value,
    position: position.value || undefined,
    work_model: workModel.value || undefined,
    salary_range: salaryRange.value.trim() || undefined,
    source_platform: sourcePlatform.value || undefined,
    source_url: sourceUrl.value.trim() || undefined,
    applied_date: appliedDate.value || undefined,
    description: description.value.trim() || undefined,
    notes: notes.value.trim() || undefined,
  };
  emit('save', payload);
  emit('update:open', false);
}
</script>

<template>
  <Dialog :open="open" @update:open="$emit('update:open', $event)">
    <DialogContent class="max-w-lg max-h-[90vh] overflow-y-auto">
      <DialogHeader>
        <DialogTitle>{{ editJob ? 'Edit Application' : 'Add Job Application' }}</DialogTitle>
      </DialogHeader>

      <div class="flex flex-col gap-4 py-2">
        <!-- Title (required) -->
        <div class="flex flex-col gap-1.5">
          <Label for="modal-title">Job Title <span class="text-destructive">*</span></Label>
          <Input id="modal-title" v-model="title" placeholder="e.g. Senior Software Engineer" />
        </div>

        <!-- Company + Location row -->
        <div class="grid grid-cols-2 gap-3">
          <div class="flex flex-col gap-1.5">
            <Label for="modal-company">Company</Label>
            <Input id="modal-company" v-model="companyName" placeholder="e.g. Acme Corp" />
          </div>
          <div class="flex flex-col gap-1.5">
            <Label for="modal-location">Location</Label>
            <Input id="modal-location" v-model="location" placeholder="e.g. New York, NY" />
          </div>
        </div>

        <!-- Status + Position row -->
        <div class="grid grid-cols-2 gap-3">
          <div class="flex flex-col gap-1.5">
            <Label>Status</Label>
            <Select v-model="status">
              <SelectTrigger>
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectGroup>
                  <SelectItem v-for="s in STATUS_OPTIONS" :key="s" :value="s">{{ s }}</SelectItem>
                </SelectGroup>
              </SelectContent>
            </Select>
          </div>
          <div class="flex flex-col gap-1.5">
            <Label>Position Level</Label>
            <Select v-model="position">
              <SelectTrigger>
                <SelectValue placeholder="Position" />
              </SelectTrigger>
              <SelectContent>
                <SelectGroup>
                  <SelectItem v-for="p in POSITION_OPTIONS" :key="p" :value="p">{{ p }}</SelectItem>
                </SelectGroup>
              </SelectContent>
            </Select>
          </div>
        </div>

        <!-- Work Model + Salary row -->
        <div class="grid grid-cols-2 gap-3">
          <div class="flex flex-col gap-1.5">
            <Label>Work Model</Label>
            <Select v-model="workModel">
              <SelectTrigger>
                <SelectValue placeholder="Work model" />
              </SelectTrigger>
              <SelectContent>
                <SelectGroup>
                  <SelectItem v-for="w in WORK_MODEL_OPTIONS" :key="w" :value="w">{{ w }}</SelectItem>
                </SelectGroup>
              </SelectContent>
            </Select>
          </div>
          <div class="flex flex-col gap-1.5">
            <Label for="modal-salary">Salary Range</Label>
            <Input id="modal-salary" v-model="salaryRange" placeholder="e.g. $80k–$120k" />
          </div>
        </div>

        <!-- Source Platform + Applied Date row -->
        <div class="grid grid-cols-2 gap-3">
          <div class="flex flex-col gap-1.5">
            <Label>Source Platform</Label>
            <Select v-model="sourcePlatform">
              <SelectTrigger>
                <SelectValue placeholder="Platform" />
              </SelectTrigger>
              <SelectContent>
                <SelectGroup>
                  <SelectItem v-for="p in PLATFORM_OPTIONS" :key="p" :value="p">{{ p }}</SelectItem>
                </SelectGroup>
              </SelectContent>
            </Select>
          </div>
          <div class="flex flex-col gap-1.5">
            <Label for="modal-date">Applied Date</Label>
            <Input id="modal-date" v-model="appliedDate" type="date" />
          </div>
        </div>

        <!-- Source URL -->
        <div class="flex flex-col gap-1.5">
          <Label for="modal-url">Job URL</Label>
          <Input id="modal-url" v-model="sourceUrl" placeholder="https://..." type="url" />
        </div>

        <!-- Description -->
        <div class="flex flex-col gap-1.5">
          <Label for="modal-desc">Job Description</Label>
          <Textarea id="modal-desc" v-model="description" placeholder="Paste job description..." class="resize-none" rows="3" />
        </div>

        <!-- Notes -->
        <div class="flex flex-col gap-1.5">
          <Label for="modal-notes">Notes</Label>
          <Textarea id="modal-notes" v-model="notes" placeholder="Personal notes..." class="resize-none" rows="2" />
        </div>
      </div>

      <DialogFooter>
        <Button variant="outline" @click="$emit('update:open', false)">Cancel</Button>
        <Button @click="handleSave" :disabled="!title.trim()">
          {{ editJob ? 'Save Changes' : 'Add Application' }}
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
