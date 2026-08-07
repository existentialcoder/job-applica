<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { toast } from '@/lib/toast'
import type { JobData, JobCreatePayload, StageData, ATSReport, BoardData } from '@/lib/types'
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue
} from '@/components/ui/select'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Filter } from 'lucide-vue-next'
import dataservice, { type JobFilters } from '@/lib/dataservice'
import { emptyJobFilters, type JobFiltersFormValues } from '@/lib/jobFilters'
import { DEFAULT_BOARD_STAGES, atsTiersFilterRange } from '@/lib/constants'
import {
  TableApplications,
  BoardApplications,
  AddJobModal,
  JobDetailPanel,
  JobFiltersPanel
} from '@/components/applications'
import { useCompaniesStore } from '@/stores/companies'
import { useExtensionLink } from '@/composables/useExtensionLink'

const companiesStore = useCompaniesStore()
const { storeUrl: extensionInstallLink } = useExtensionLink()

const props = defineProps<{
  boardId?: number
  stages?: StageData[]
  defaultStatus?: string
}>()

const emit = defineEmits<{
  (e: 'stages-updated', stages: StageData[]): void
}>()

const selectedLayout = ref<'list' | 'board'>('list')

const allJobs = ref<JobData[]>([])
const totalJobs = ref(0)
const isLoading = ref(false)
const filtersApplied = ref(false)

const selectedJobs = ref<JobData[]>([])
const isModalOpen = ref(false) // add new job modal
const isPanelOpen = ref(false) // job detail slide-over
const editingJob = ref<JobData | null>(null)
const panelInitialTab = ref<'details' | 'ats'>('details')

const searchQuery = ref('')
const filterPlatform = ref('__all__')
const currentPage = ref(1)
const pageSize = 20

const isFiltersPanelOpen = ref(false)
const jobFilters = reactive<JobFiltersFormValues>(emptyJobFilters())
const boardOptions = ref<{ label: string; value: string }[]>([])

const statusOptions = ref<string[]>(
  props.stages?.map((s) => s.label) ?? DEFAULT_BOARD_STAGES.map((s) => s.label)
)

watch(
  () => props.stages,
  (stages) => {
    if (stages?.length) statusOptions.value = stages.map((s) => s.label)
  },
  { immediate: true }
)

const LIST_FILTER_KEY_MAP = [
  ['status', 'status'],
  ['country', 'country'],
  ['company', 'company'],
  ['workModel', 'work_model'],
  ['position', 'position']
] as const

async function loadJobs() {
  isLoading.value = true
  const filters: JobFilters = {
    page: currentPage.value,
    per_page: pageSize
  }
  if (searchQuery.value.trim()) filters.query = searchQuery.value.trim()
  if (filterPlatform.value && filterPlatform.value !== '__all__')
    filters.source_platform = filterPlatform.value

  if (props.boardId) {
    filters.board_id = props.boardId
  } else if (jobFilters.boardIds.length) {
    filters.board_ids = jobFilters.boardIds.join(',')
  }

  for (const [formKey, apiKey] of LIST_FILTER_KEY_MAP) {
    const values = jobFilters[formKey]
    if (values.length) filters[apiKey] = values.join(',')
  }

  if (jobFilters.city.trim()) filters.city = jobFilters.city.trim()
  if (jobFilters.appliedRange.from) filters.applied_from = jobFilters.appliedRange.from
  if (jobFilters.appliedRange.to) filters.applied_to = jobFilters.appliedRange.to
  if (jobFilters.createdRange.from) filters.created_from = jobFilters.createdRange.from
  if (jobFilters.createdRange.to) filters.created_to = jobFilters.createdRange.to
  const atsRange = atsTiersFilterRange(jobFilters.atsScoreTiers)
  if (atsRange) {
    filters.ats_score_min = atsRange.min
    filters.ats_score_max = atsRange.max
  }

  const res = await dataservice.getJobs(filters)
  allJobs.value = res.items
  totalJobs.value = res.total
  isLoading.value = false
}

function onFiltersApplied(next: JobFiltersFormValues) {
  filtersApplied.value = true
  Object.assign(jobFilters, next)
  currentPage.value = 1
  loadJobs()
}

watch([searchQuery, filterPlatform], () => {
  currentPage.value = 1
  loadJobs()
})

function onTableSelectionChange(val: JobData[]) {
  selectedJobs.value = val
}

async function deleteSelectedJobs() {
  if (selectedJobs.value.length === 0) return
  const count = selectedJobs.value.length
  try {
    await Promise.all(selectedJobs.value.map((job) => dataservice.deleteJob(job.id)))
    selectedJobs.value = []
    await loadJobs()
    toast.success(`${count} job${count > 1 ? 's' : ''} deleted`)
  } catch {
    toast.error('Failed to delete selected jobs')
  }
}

function openAddModal() {
  editingJob.value = null
  isModalOpen.value = true
}

function openEditModal(job: JobData, tab: 'details' | 'ats' = 'details') {
  editingJob.value = job
  panelInitialTab.value = tab
  isPanelOpen.value = true
  router.replace({ query: { ...route.query, job: String(job.id), tab } })
}

function handlePanelTabChange(tab: 'details' | 'ats') {
  router.replace({ query: { ...route.query, tab } })
}

watch(isPanelOpen, (open) => {
  if (!open) {
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const { job: _j, tab: _t, ...rest } = route.query
    router.replace({ query: rest })
  }
})

async function handleSaveJob(payload: JobCreatePayload) {
  if (props.boardId) payload = { ...payload, board_id: props.boardId }
  try {
    await dataservice.createJob(payload)
    await companiesStore.refresh()
    await loadJobs()
    toast.success('Job added successfully')
  } catch {
    toast.error('Failed to add job')
  }
}

async function handleSaveEdit(jobId: number, payload: JobCreatePayload) {
  if (props.boardId && payload.board_id === undefined)
    payload = { ...payload, board_id: props.boardId }
  const updatedJob = await dataservice.updateJob(jobId, payload)
  if (updatedJob) {
    await companiesStore.refresh()
    toast.success('Job updated successfully')
    await loadJobs()
  } else {
    toast.error('Failed to update job')
  }
}

function handleScoreUpdated(jobId: number, update: { ats_score: number; ats_report: ATSReport }) {
  if (editingJob.value?.id === jobId) {
    editingJob.value = { ...editingJob.value, ...update }
  }
}

async function handleStatusChange(jobId: number, newStatus: string) {
  const idx = allJobs.value.findIndex((j) => j.id === jobId)
  const prevStatus = allJobs.value[idx]?.status
  const today = new Date().toISOString().slice(0, 10)
  const autoDate = newStatus === 'Applied' && !allJobs.value[idx]?.applied_date ? today : undefined
  if (idx !== -1)
    allJobs.value[idx] = {
      ...allJobs.value[idx],
      status: newStatus,
      ...(autoDate ? { applied_date: autoDate } : {})
    }
  try {
    const updated = await dataservice.updateJob(jobId, {
      status: newStatus,
      ...(autoDate ? { applied_date: autoDate } : {})
    })
    if (!updated && idx !== -1 && prevStatus !== undefined) {
      allJobs.value[idx] = { ...allJobs.value[idx], status: prevStatus }
      toast.error('Failed to update status')
    }
  } catch {
    if (idx !== -1 && prevStatus !== undefined) {
      allJobs.value[idx] = { ...allJobs.value[idx], status: prevStatus }
    }
    toast.error('Failed to update status')
  }
}

async function handleDeleteJob(jobId: number) {
  try {
    await dataservice.deleteJob(jobId)
    await loadJobs()
    toast.success('Job deleted')
  } catch {
    toast.error('Failed to delete job')
  }
}

async function handleAddStage(stage: StageData) {
  if (!props.boardId || !props.stages) return
  const newStages = [...props.stages, stage]
  try {
    const updated = await dataservice.updateBoard(props.boardId, { stages: newStages })
    if (updated) emit('stages-updated', updated.stages)
    else toast.error('Failed to add stage')
  } catch {
    toast.error('Failed to add stage')
  }
}

async function handleRemoveStage(key: string) {
  if (!props.boardId || !props.stages) return
  const newStages = props.stages.filter((s) => s.key !== key)
  if (newStages.length === 0) return
  try {
    const updated = await dataservice.updateBoard(props.boardId, { stages: newStages })
    if (updated) {
      emit('stages-updated', updated.stages)
      await loadJobs()
    } else {
      toast.error('Failed to remove stage')
    }
  } catch {
    toast.error('Failed to remove stage')
  }
}

async function handleUpdateStage(payload: { oldKey: string; stage: StageData }) {
  if (!props.boardId || !props.stages) return
  const { oldKey, stage } = payload
  const newStages = props.stages.map((s) => (s.key === oldKey ? stage : s))
  const keyRenames = oldKey !== stage.key ? { [oldKey]: stage.key } : undefined
  const updated = await dataservice.updateBoard(props.boardId, {
    stages: newStages,
    key_renames: keyRenames
  })
  if (updated) {
    emit('stages-updated', updated.stages)
    if (keyRenames) await loadJobs()
  }
}

async function handleQuickAddJob(payload: {
  title: string
  company_name?: string
  status: string
  work_model?: string
}) {
  const fullPayload: JobCreatePayload = {
    title: payload.title,
    company_name: payload.company_name,
    status: payload.status,
    work_model: payload.work_model,
    board_id: props.boardId
  }
  try {
    await dataservice.createJob(fullPayload)
    await companiesStore.refresh()
    await loadJobs()
    toast.success('Job added')
  } catch {
    toast.error('Failed to add job')
  }
}

function clearFilters() {
  filtersApplied.value = false
  searchQuery.value = ''
  filterPlatform.value = '__all__'
  Object.assign(jobFilters, emptyJobFilters())
  currentPage.value = 1
  loadJobs()
}

const hasActiveFilters = () =>
  !!(
    searchQuery.value ||
    (filterPlatform.value && filterPlatform.value !== '__all__') ||
    jobFilters.boardIds.length ||
    jobFilters.status.length ||
    jobFilters.city.trim() ||
    jobFilters.country.length ||
    jobFilters.company.length ||
    jobFilters.workModel.length ||
    jobFilters.position.length ||
    jobFilters.appliedRange.from ||
    jobFilters.appliedRange.to ||
    jobFilters.createdRange.from ||
    jobFilters.createdRange.to ||
    jobFilters.atsScoreTiers.length
  )

const route = useRoute()
const router = useRouter()

onMounted(async () => {
  const settings = await dataservice.getSettings()
  if (settings.view_mode === 'board' || settings.view_mode === 'list') {
    selectedLayout.value = settings.view_mode as 'list' | 'board'
  }
  if (settings.saved_job_filters && typeof settings.saved_job_filters === 'object') {
    Object.assign(jobFilters, emptyJobFilters(), settings.saved_job_filters)
  }
  if (!props.boardId) {
    const boards: BoardData[] = await dataservice.getBoards()
    boardOptions.value = boards.map((b) => ({ label: b.name, value: String(b.id) }))
  }
  companiesStore.fetch()
  if (route.query.query) {
    searchQuery.value = route.query.query as string
  }
  await loadJobs()
  if (route.query.job) {
    const job = await dataservice.getJob(Number(route.query.job))
    const tab = route.query.tab === 'ats' ? 'ats' : 'details'
    if (job) openEditModal(job, tab)
  }
})

watch(selectedLayout, (val) => {
  dataservice.updateSettings({ view_mode: val })
})
</script>

<template>
  <div class="flex flex-col gap-4">
    <!-- Top toolbar -->
    <div class="flex flex-wrap items-center justify-between gap-3">
      <!-- Left: Search + Filters -->
      <div class="flex flex-wrap items-center gap-2 flex-1">
        <Input v-model="searchQuery" placeholder="Search jobs..." class="w-48" />
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
            Edit
          </Button>
          <Button size="sm" variant="destructive" @click="deleteSelectedJobs">
            <Icon name="Trash" class="w-4 h-4 mr-1" />
            Delete
          </Button>
        </div>
        <Button
          size="sm"
          variant="outline"
          class="relative"
          title="Filter jobs"
          @click="isFiltersPanelOpen = true"
        >
          <Filter class="w-4 h-4" />
          <span
            v-if="hasActiveFilters()"
            class="absolute -top-1 -right-1 w-2 h-2 rounded-full bg-primary"
          />
        </Button>
        <Button size="sm" @click="openAddModal">Add Job</Button>
        <div class="flex items-center gap-1">
          <Label class="text-sm text-muted-foreground">View:</Label>
          <Select v-model="selectedLayout" class="w-28">
            <SelectTrigger class="w-28">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectGroup>
                <SelectItem value="list">List</SelectItem>
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

    <!-- Loading skeleton -->
    <div v-if="isLoading">
      <!-- Table skeleton -->
      <div v-if="selectedLayout === 'list'" class="rounded-md border border-border overflow-hidden">
        <div
          class="bg-muted/40 px-4 py-2.5 grid grid-cols-[2rem_1fr_10rem_7rem_7rem_6rem] gap-3 border-b border-border"
        >
          <div class="h-3 w-3 rounded bg-muted animate-pulse self-center"></div>
          <div class="h-3 w-24 rounded bg-muted animate-pulse"></div>
          <div class="h-3 w-16 rounded bg-muted animate-pulse"></div>
          <div class="h-3 w-14 rounded bg-muted animate-pulse"></div>
          <div class="h-3 w-12 rounded bg-muted animate-pulse"></div>
          <div class="h-3 w-10 rounded bg-muted animate-pulse"></div>
        </div>
        <div
          v-for="i in 8"
          :key="i"
          class="px-4 py-3 grid grid-cols-[2rem_1fr_10rem_7rem_7rem_6rem] gap-3 border-b border-border last:border-0"
        >
          <div class="h-4 w-4 rounded bg-muted animate-pulse self-center"></div>
          <div class="flex flex-col gap-1.5">
            <div
              class="h-3.5 rounded bg-muted animate-pulse"
              :style="{ width: `${55 + ((i * 13) % 35)}%` }"
            ></div>
            <div class="h-2.5 w-24 rounded bg-muted/60 animate-pulse"></div>
          </div>
          <div
            class="h-3 rounded bg-muted animate-pulse self-center"
            :style="{ width: `${50 + ((i * 17) % 40)}%` }"
          ></div>
          <div class="h-6 w-20 rounded-full bg-muted animate-pulse self-center"></div>
          <div class="h-3 w-16 rounded bg-muted animate-pulse self-center"></div>
          <div class="h-3 w-8 rounded bg-muted animate-pulse self-center"></div>
        </div>
      </div>
      <!-- Board skeleton -->
      <div v-else class="flex gap-4 overflow-x-auto pb-2">
        <div v-for="col in 5" :key="col" class="flex-shrink-0 w-64 flex flex-col gap-2">
          <div class="h-8 rounded-lg bg-muted animate-pulse"></div>
          <div
            v-for="card in 3"
            :key="card"
            class="rounded-lg border border-border bg-card p-3 flex flex-col gap-2"
          >
            <div
              class="h-3.5 rounded bg-muted animate-pulse"
              :style="{ width: `${60 + ((card * 19) % 35)}%` }"
            ></div>
            <div class="h-2.5 w-20 rounded bg-muted/60 animate-pulse"></div>
            <div class="h-2.5 w-14 rounded bg-muted/40 animate-pulse"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty state -->
    <div
      v-else-if="allJobs.length === 0"
      class="flex flex-col items-center justify-center py-16 gap-3 text-center"
    >
      <svg
        class="w-12 h-12 text-muted-foreground/30"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="1.5"
          d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
        />
      </svg>
      <p class="text-muted-foreground font-medium">
        No applications {{ filtersApplied ? 'matching your filters.' : 'tracked yet.' }}
      </p>
      <p class="text-sm text-muted-foreground">
        {{ filtersApplied ? 'Try adjusting your filters or search query.' : `Click "Add Job" or use
        the
        <a href="${extensionInstallLink}" class="text-primary hover:underline">browser extension</a>
        to start tracking your applications.` }}
      </p>
    </div>

    <!-- Table view -->
    <TableApplications
      v-else-if="selectedLayout === 'list'"
      :jobs="allJobs"
      :status-options="statusOptions"
      @selection-change="onTableSelectionChange"
      @edit="openEditModal"
      @status-change="handleStatusChange"
      @add-quick="handleQuickAddJob"
    />

    <!-- Board view -->
    <BoardApplications
      v-else-if="selectedLayout === 'board'"
      :jobs="allJobs"
      :stages="stages"
      @edit="openEditModal"
      @status-change="handleStatusChange"
      @delete="handleDeleteJob"
      @add-stage="handleAddStage"
      @remove-stage="handleRemoveStage"
      @update-stage="handleUpdateStage"
      @add-job="handleQuickAddJob"
    />

    <!-- Add job modal (new job only) -->
    <AddJobModal
      v-model:open="isModalOpen"
      :status-options="statusOptions"
      :default-status="defaultStatus ?? statusOptions[0]"
      @save="handleSaveJob"
    />

    <!-- Job detail slide-over (view/edit existing) -->
    <JobDetailPanel
      v-model:open="isPanelOpen"
      :job="editingJob"
      :status-options="statusOptions"
      :initial-tab="panelInitialTab"
      @save="handleSaveEdit"
      @tab-change="handlePanelTabChange"
      @score-updated="handleScoreUpdated"
    />

    <!-- Filters side panel -->
    <JobFiltersPanel
      v-model:open="isFiltersPanelOpen"
      :model-value="jobFilters"
      :status-options="statusOptions"
      :board-options="boardOptions"
      @update:model-value="onFiltersApplied"
    />
  </div>
</template>
