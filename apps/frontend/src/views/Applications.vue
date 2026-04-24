<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import type { JobData, JobCreatePayload } from '@/lib/types';
import {
  Select, SelectContent, SelectGroup, SelectItem, SelectTrigger, SelectValue,
} from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import dataservice, { type JobFilters } from '@/lib/dataservice';
import { TableApplications, BoardApplications, AddJobModal } from '@/components/applications';

const selectedLayout = ref<'table' | 'board'>('table');
const allJobs = ref<JobData[]>([]);
const totalJobs = ref(0);
const isLoading = ref(false);

const selectedJobs = ref<JobData[]>([]);
const isModalOpen = ref(false);
const editingJob = ref<JobData | null>(null);

const searchQuery = ref('');
const filterStatus = ref('');
const filterPlatform = ref('');
const currentPage = ref(1);
const pageSize = 20;

const STATUS_OPTIONS = ['Saved', 'Applied', 'Phone Screen', 'Interview', 'Technical', 'Offer', 'Rejected', 'Withdrawn'];
const PLATFORM_OPTIONS = ['LinkedIn', 'Indeed', 'Glassdoor', 'Monster', 'ZipRecruiter', 'Jobscan', 'Other'];

async function loadJobs() {
  isLoading.value = true;
  const filters: JobFilters = {
    page: currentPage.value,
    per_page: pageSize,
  };
  if (searchQuery.value.trim()) filters.query = searchQuery.value.trim();
  if (filterStatus.value) filters.status = filterStatus.value;
  if (filterPlatform.value) filters.source_platform = filterPlatform.value;

  const res = await dataservice.getJobs(filters);
  allJobs.value = res.items;
  totalJobs.value = res.total;
  isLoading.value = false;
}

watch([searchQuery, filterStatus, filterPlatform], () => {
  currentPage.value = 1;
  loadJobs();
});

function onTableSelectionChange(val: JobData[]) {
  selectedJobs.value = val;
}

async function deleteSelectedJobs() {
  if (selectedJobs.value.length === 0) return;
  await Promise.all(selectedJobs.value.map((job) => dataservice.deleteJob(job.id)));
  selectedJobs.value = [];
  await loadJobs();
}

function openAddModal() {
  editingJob.value = null;
  isModalOpen.value = true;
}

function openEditModal(job: JobData) {
  editingJob.value = job;
  isModalOpen.value = true;
}

async function handleSaveJob(payload: JobCreatePayload) {
  if (editingJob.value) {
    await dataservice.updateJob(editingJob.value.id, payload);
  } else {
    await dataservice.createJob(payload);
  }
  await loadJobs();
}

async function handleStatusChange(jobId: number, newStatus: string) {
  await dataservice.updateJob(jobId, { status: newStatus });
  await loadJobs();
}

function clearFilters() {
  searchQuery.value = '';
  filterStatus.value = '';
  filterPlatform.value = '';
}

const hasActiveFilters = () => !!(searchQuery.value || filterStatus.value || filterPlatform.value);

const route = useRoute();

onMounted(async () => {
  if (route.query.query) {
    searchQuery.value = route.query.query as string;
  }
  await loadJobs();
  if (route.query.job) {
    const job = await dataservice.getJob(Number(route.query.job));
    if (job) openEditModal(job);
  }
});
</script>

<template>
  <div class="flex flex-col gap-4">
    <!-- Top toolbar -->
    <div class="flex flex-wrap items-center justify-between gap-3">
      <!-- Left: Search + Filters -->
      <div class="flex flex-wrap items-center gap-2 flex-1">
        <Input
          v-model="searchQuery"
          placeholder="Search jobs..."
          class="w-48"
        />
        <Select v-model="filterStatus">
          <SelectTrigger class="w-36">
            <SelectValue placeholder="All Statuses" />
          </SelectTrigger>
          <SelectContent>
            <SelectGroup>
              <SelectItem value="">All Statuses</SelectItem>
              <SelectItem v-for="s in STATUS_OPTIONS" :key="s" :value="s">{{ s }}</SelectItem>
            </SelectGroup>
          </SelectContent>
        </Select>
        <Select v-model="filterPlatform">
          <SelectTrigger class="w-36">
            <SelectValue placeholder="All Platforms" />
          </SelectTrigger>
          <SelectContent>
            <SelectGroup>
              <SelectItem value="">All Platforms</SelectItem>
              <SelectItem v-for="p in PLATFORM_OPTIONS" :key="p" :value="p">{{ p }}</SelectItem>
            </SelectGroup>
          </SelectContent>
        </Select>
        <Button v-if="hasActiveFilters()" variant="ghost" size="sm" @click="clearFilters">
          Clear filters
        </Button>
      </div>

      <!-- Right: Actions + Layout toggle -->
      <div class="flex items-center gap-2">
        <div v-if="selectedJobs.length > 0" class="flex items-center gap-2">
          <span class="text-sm text-muted-foreground">{{ selectedJobs.length }} selected</span>
          <Button
            v-if="selectedJobs.length === 1"
            size="sm"
            variant="outline"
            @click="openEditModal(selectedJobs[0])"
          >
            <Icon name="Edit" class="w-4 h-4 mr-1" />
            Edit
          </Button>
          <Button size="sm" variant="destructive" @click="deleteSelectedJobs">
            <Icon name="Trash" class="w-4 h-4 mr-1" />
            Delete
          </Button>
        </div>
        <Button size="sm" @click="openAddModal">
          <Icon name="Plus" class="w-4 h-4 mr-1" />
          Add Job
        </Button>
        <div class="flex items-center gap-1">
          <Label class="text-sm text-muted-foreground">View:</Label>
          <Select v-model="selectedLayout" class="w-28">
            <SelectTrigger class="w-28">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectGroup>
                <SelectItem value="table">Table</SelectItem>
                <SelectItem value="board">Board</SelectItem>
              </SelectGroup>
            </SelectContent>
          </Select>
        </div>
      </div>
    </div>

    <!-- Stats row -->
    <div v-if="totalJobs > 0" class="text-sm text-muted-foreground">
      Showing {{ allJobs.length }} of {{ totalJobs }} applications
    </div>

    <!-- Loading state -->
    <div v-if="isLoading" class="flex justify-center py-12">
      <svg class="w-6 h-6 animate-spin text-muted-foreground" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
      </svg>
    </div>

    <!-- Empty state -->
    <div v-else-if="allJobs.length === 0 && !isLoading" class="flex flex-col items-center justify-center py-16 gap-3 text-center">
      <svg class="w-12 h-12 text-muted-foreground/30" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
          d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
      </svg>
      <p class="text-muted-foreground font-medium">No applications yet</p>
      <p class="text-sm text-muted-foreground">Add a job manually or use the browser extension to capture from job boards.</p>
      <Button @click="openAddModal" size="sm">
        <Icon name="Plus" class="w-4 h-4 mr-1" />
        Add First Application
      </Button>
    </div>

    <!-- Table view -->
    <TableApplications
      v-else-if="selectedLayout === 'table' && !isLoading"
      :jobs="allJobs"
      @selection-change="onTableSelectionChange"
      @edit="openEditModal"
      @status-change="handleStatusChange"
    />

    <!-- Board view -->
    <BoardApplications
      v-else-if="selectedLayout === 'board' && !isLoading"
      :jobs="allJobs"
      @edit="openEditModal"
      @status-change="handleStatusChange"
    />

    <!-- Add/Edit modal -->
    <AddJobModal
      v-model:open="isModalOpen"
      :edit-job="editingJob"
      @save="handleSaveJob"
    />
  </div>
</template>
