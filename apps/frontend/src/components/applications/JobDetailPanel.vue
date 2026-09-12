<script setup lang="ts">
import { AtsGauge } from '@job-applica/ui';
import { ref, computed, watch, onMounted, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { Button } from '@/components/ui/button';
import { Combobox } from '@/components/ui/combobox';
import { DatePicker } from '@/components/ui/date-picker';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue
} from '@/components/ui/select';
import { Sheet, SheetContent, SheetTitle } from '@/components/ui/sheet';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Textarea } from '@/components/ui/textarea';
import { Timeline, TimelineContent, TimelineDot, TimelineItem, TimelineTime, TimelineTitle } from '@/components/ui/timeline';
import {
  ATS_SCORE_TIERS,
  COUNTRY_OPTIONS,
  DEFAULT_COMPANY_LOGO_URL,
  DEFAULT_BOARD_STAGES
} from '@/lib/constants';
import dataservice from '@/lib/dataservice';
import { findStage } from '@/lib/stages';
import { toast } from '@/lib/toast';
import type { JobData, JobCreatePayload, AtsTier, JobTimeline, ATSReport } from '@/lib/types';
import { useBoardsStore } from '@/stores/boards.js';
import { useCompaniesStore } from '@/stores/companies';
import { useResumesStore } from '@/stores/resumes.js';
import CompanyCombobox from './CompanyCombobox.vue';
import StageBadge from './StageBadge.vue';

const COUNTRY_COMBOBOX_OPTIONS = COUNTRY_OPTIONS.map((c) => ({ label: c, value: c }));

const router = useRouter();
const companiesStore = useCompaniesStore();
const boardsStore = useBoardsStore();
const resumesStore = useResumesStore();

const props = defineProps<{
  open: boolean;
  job?: JobData | null;
  statusOptions?: string[];
  initialTab?: 'details' | 'ats';
}>();

const emit = defineEmits<{
  (e: 'update:open', val: boolean): void;
  (e: 'save', id: number, payload: JobCreatePayload): void;
  (e: 'tab-change', tab: 'details' | 'ats'): void;
  (e: 'score-updated', jobId: number, update: { ats_score: number; ats_report: ATSReport }): void;
}>();

const POSITION_OPTIONS = ['Intern', 'Junior', 'Mid', 'Senior', 'Lead', 'Manager'];
const WORK_MODEL_OPTIONS = ['On-site', 'Remote', 'Hybrid'];
const PLATFORM_OPTIONS = [
  'LinkedIn',
  'Indeed',
  'Glassdoor',
  'Monster',
  'ZipRecruiter',
  'Jobscan',
  'Other'
];

const activeTab = ref<'details' | 'ats' | 'timeline'>('details');

const title = ref('');
const companyName = ref('');
const locationCity = ref('');
const locationCountry = ref('');
const boardId = ref<number | undefined>(undefined);
const status = ref('');
const position = ref('');
const workModel = ref('');
const salaryRange = ref('');
const sourcePlatform = ref('');
const sourceUrl = ref('');
const appliedDate = ref('');
const description = ref('');
const notes = ref('');
const jobTimeline = ref<JobTimeline[] | null>(null);
const jobTimelineLoading = ref(false);

function getAtsTier(score: number): AtsTier {
  for (let i = ATS_SCORE_TIERS.length - 1; i >= 0; i--) {
    if (score >= ATS_SCORE_TIERS[i].min) return ATS_SCORE_TIERS[i];
  }
  return ATS_SCORE_TIERS[0];
}

watch(status, (newVal) => {
  if (newVal === 'Applied' && !appliedDate.value) {
    appliedDate.value = new Date().toISOString().slice(0, 10);
  }
});

onMounted(async () => {
  await companiesStore.fetch();
});

function onBoardSelectOpenChange(open: boolean) {
  if (open) {
    boardsStore.fetch();
  }
}

const boardOptions = computed(() =>
  boardsStore.boards.map((b) => ({ label: b.name, value: String(b.id) }))
);

const currentBoardStageLabels = computed(() => {
  const currentBoard = boardsStore.boards.find((b) => b.id === boardId.value);
  if (currentBoard?.stages.length) return currentBoard.stages.map((s) => s.label);
  return props.statusOptions?.length
    ? props.statusOptions
    : DEFAULT_BOARD_STAGES.map((s) => s.label);
});

function onBoardChange(val: string) {
  boardId.value = Number(val);
  if (!currentBoardStageLabels.value.includes(status.value)) {
    status.value = currentBoardStageLabels.value[0] ?? 'Saved';
  }
}

const isEditingUrl = ref(false);
const pendingUrl = ref('');
const urlInputRef = ref<HTMLInputElement | null>(null);

function startEditUrl() {
  pendingUrl.value = sourceUrl.value;
  isEditingUrl.value = true;
  nextTick(() => urlInputRef.value?.focus());
}

function confirmUrl() {
  sourceUrl.value = pendingUrl.value.trim();
  isEditingUrl.value = false;
}

function cancelUrl() {
  isEditingUrl.value = false;
}

const selectedResumeId = ref<string>('');
const atsReport = ref<ATSReport | null>(null);
const isScoring = ref(false);

const selectedResumeName = computed(() => {
  if (!selectedResumeId.value) return '';
  const r = resumesStore.resumes.find((r) => String(r.id) === selectedResumeId.value);
  return r?.original_name ?? '';
});

const hasDescription = computed(() => !!description.value.trim());
const hasLinkedCv = computed(() => !!selectedResumeId.value);
const canScore = computed(() => hasDescription.value && hasLinkedCv.value && !isScoring.value);

function atsScoreColor(score: number) {
  return getAtsTier(score).color;
}

function atsTierLabel(score: number) {
  const tier = getAtsTier(score);
  return { label: tier.label, cls: tier.badgeClass };
}

async function loadResumes() {
  await resumesStore.fetch();
  if (props.job?.ats_resume_id) {
    selectedResumeId.value = String(props.job.ats_resume_id);
  } else {
    const def = resumesStore.resumes.find((r) => (r as any).is_default);
    selectedResumeId.value = def ? String(def.id) : resumesStore.resumes.length ? String(resumesStore.resumes[0].id) : '';
  }
}

async function loadJobTimeline() {
  jobTimelineLoading.value = true;
  jobTimeline.value = await dataservice.getJobTimeline(props.job?.id);
  jobTimelineLoading.value = false;
}

async function calculateScore() {
  if (!props.job || !canScore.value) return;
  isScoring.value = true;
  try {
    const report = await dataservice.calculateAtsScore(
      props.job.id,
      selectedResumeId.value ? Number(selectedResumeId.value) : null
    );
    atsReport.value = report;
    emit('score-updated', props.job.id, { ats_score: report.score, ats_report: report });
    toast.success(`Match score: ${Math.round(report.score)}/100`);
  } catch (err: any) {
    toast.error(err.message ?? 'Scoring failed');
  } finally {
    isScoring.value = false;
  }
}

watch(activeTab, (tab) => {
  emit('tab-change', tab);
  if (tab === 'ats') {
    loadResumes();
  }

  if (tab === 'timeline') {
    loadJobTimeline();
  }
});

watch(
  () => props.open,
  (open) => {
    if (!open) {
      isEditingUrl.value = false;
      atsReport.value = null;
      selectedResumeId.value = '';
      return;
    }
    activeTab.value = props.initialTab ?? 'details';
    const job = props.job;
    if (!job) {
      return;
    }
    title.value = job.title || '';
    companyName.value = job.company?.name || '';
    locationCity.value = job.location?.city || '';
    locationCountry.value = job.location?.country || '';
    boardId.value = job.board_id;
    status.value = job.status || 'Saved';
    position.value = job.position || '';
    workModel.value = job.work_model || '';
    salaryRange.value = job.salary_range || '';
    sourcePlatform.value = job.source_platform || '';
    sourceUrl.value = job.source_url || '';
    appliedDate.value = job.applied_date || '';
    description.value = job.description || '';
    notes.value = job.notes || '';

    // Restore persisted ATS report
    if (job.ats_report) {
      atsReport.value = job.ats_report as ATSReport;
    }

    if (activeTab.value === 'ats') {
      loadResumes();
    }
  }
);

function handleSave() {
  if (!props.job || !title.value.trim() || !companyName.value.trim()) return;
  const city = locationCity.value.trim();
  const country = locationCountry.value.trim();
  emit('save', props.job.id, {
    title: title.value.trim(),
    company_name: companyName.value.trim() || undefined,
    location:
      city || country ? { city: city || undefined, country: country || undefined } : undefined,
    board_id: boardId.value,
    status: status.value,
    position: position.value || undefined,
    work_model: workModel.value || undefined,
    salary_range: salaryRange.value.trim() || undefined,
    source_platform: sourcePlatform.value || undefined,
    source_url: sourceUrl.value.trim() || undefined,
    applied_date: appliedDate.value || undefined,
    description: description.value.trim() || undefined,
    notes: notes.value.trim() || undefined
  });
}

const timelineStates = computed(() => {
  if (jobTimeline.value?.length) {
    const result = jobTimeline.value.map(timeline => {
      const targetStatus = findStage(boardsStore.boards, props.job?.board_id, timeline.to_status);

      return {
        label: targetStatus?.label,
        color: targetStatus?.color,
        ts: timeline.created_at
      };
    });

    const targetStatus = findStage(boardsStore.boards, props.job?.board_id, jobTimeline.value[0].from_status);

    if (!targetStatus) {
      return result;
    }

    return [
      {
        label: targetStatus?.label,
        color: targetStatus?.color,
        ts: props.job?.created_at
      },
      ...result
    ];
  }
  return null;
});

function formatTimelineDate(iso?: string): string {
  if (!iso) {
    return '';
  }
  return new Date(iso).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}

const currentStatusStage = computed(() =>
  findStage(boardsStore.boards, props.job?.board_id, props.job?.status) ?? null
);
</script>

<template>
  <Sheet :open="open" @update:open="$emit('update:open', $event)">
    <SheetContent side="right" class="!w-[40vw] !max-w-[40vw] !p-0 !gap-0">
      <div style="display: flex; flex-direction: column; height: 100vh; overflow: hidden">
        <div class="flex items-start gap-3 px-5 pt-5 pb-4 border-b" style="flex-shrink: 0">
          <!-- Company logo avatar -->
          <div
            v-if="job?.company"
            class="flex-shrink-0 w-10 h-10 rounded-full bg-muted flex items-center justify-center overflow-hidden border border-border"
          >
            <img
              :src="job.company.logo_url || DEFAULT_COMPANY_LOGO_URL"
              class="w-full h-full object-contain"
              @error="($event.target as HTMLImageElement).src = DEFAULT_COMPANY_LOGO_URL"
            />
          </div>

          <div class="flex-1 min-w-0">
            <SheetTitle class="text-base font-semibold leading-snug truncate">
              {{ job?.title || 'Job Detail' }}
            </SheetTitle>

            <div class="flex items-center gap-2 mt-0.5 flex-wrap">
              <span v-if="job?.company" class="text-sm text-muted-foreground">{{
                job.company.name
              }}</span>
              <span v-if="job?.company && job?.status" class="text-muted-foreground/40 text-sm"
                >·</span
              >
              <StageBadge v-if="job?.status" :color="currentStatusStage?.color" :label="job.status" />
            </div>

            <!-- ── Inline URL editor ─────────────────────────────────────────── -->
            <div class="flex items-center gap-1.5 mt-1.5 min-w-0">
              <template v-if="isEditingUrl">
                <input
                  ref="urlInputRef"
                  v-model="pendingUrl"
                  type="url"
                  placeholder="https://..."
                  class="flex-1 min-w-0 text-xs h-6 px-2 rounded border border-input bg-transparent focus:outline-none focus:ring-1 focus:ring-ring"
                  @keydown.enter="confirmUrl"
                  @keydown.escape="cancelUrl"
                />
                <button
                  class="flex-shrink-0 text-green-500 hover:text-green-400 transition-colors p-0.5"
                  title="Confirm"
                  @click="confirmUrl"
                >
                  <Icon name="Check" :size="14" :stroke-width="2.5" />
                </button>
                <button
                  class="flex-shrink-0 text-muted-foreground hover:text-foreground transition-colors p-0.5"
                  title="Cancel"
                  @click="cancelUrl"
                >
                  <Icon name="X" :size="14" :stroke-width="2.5" />
                </button>
              </template>

              <template v-else-if="sourceUrl">
                <a
                  :href="sourceUrl"
                  target="_blank"
                  rel="noopener"
                  class="flex items-center gap-1 text-xs text-primary hover:underline flex-shrink-0"
                  :title="sourceUrl"
                >
                  <Icon name="ExternalLink" :size="12" />
                  Job URL
                </a>
                <button
                  class="flex-shrink-0 text-muted-foreground hover:text-foreground transition-colors p-0.5"
                  title="Edit link"
                  @click="startEditUrl"
                >
                  <Icon name="Pencil" :size="12" />
                </button>
              </template>

              <button
                v-else
                class="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors"
                @click="startEditUrl"
              >
                <Icon name="Link2" :size="12" />
                Add link
              </button>
            </div>
          </div>

          <button
            class="flex-shrink-0 p-1.5 rounded-md text-muted-foreground hover:text-foreground hover:bg-muted transition-colors mt-0.5"
            aria-label="Close"
            @click="$emit('update:open', false)"
          >
            <Icon name="X" :size="16" />
          </button>
        </div>

        <div class="px-5 pt-3 pb-3 border-b" style="flex-shrink: 0">
          <Tabs v-model="activeTab">
            <TabsList>
              <TabsTrigger value="details">Details</TabsTrigger>
              <TabsTrigger value="ats">
                Match Score
                <span
                  v-if="job?.ats_score != null"
                  class="ml-1.5 text-[10px] font-bold px-1.5 py-0.5 rounded-full"
                  :class="atsTierLabel(job.ats_score).cls"
                  >{{ Math.round(job.ats_score) }}</span
                >
              </TabsTrigger>
              <TabsTrigger value="timeline">Timeline</TabsTrigger>
            </TabsList>
          </Tabs>
        </div>

        <div style="flex: 1; min-height: 0; overflow-y: auto">
          <div v-show="activeTab === 'details'" class="px-5 py-4 space-y-4">
            <div class="space-y-1.5">
              <Label>Job Title <span class="text-destructive">*</span></Label>
              <Input v-model="title" placeholder="e.g. Senior Software Engineer" />
            </div>

            <div class="space-y-1.5">
              <Label>Company <span class="text-destructive">*</span></Label>
              <CompanyCombobox
                :companies="companiesStore.companies"
                v-model="companyName"
                placeholder="e.g. Acme Corp"
              />
            </div>

            <div class="grid grid-cols-2 gap-3">
              <div class="space-y-1.5">
                <Label>City</Label>
                <Input v-model="locationCity" placeholder="e.g. New York" />
              </div>
              <div class="space-y-1.5">
                <Label>Country</Label>
                <Combobox
                  v-model="locationCountry"
                  :options="COUNTRY_COMBOBOX_OPTIONS"
                  placeholder="Select country"
                />
              </div>
            </div>

            <div class="space-y-1.5">
              <Label>Board</Label>
              <Select
                :model-value="boardId != null ? String(boardId) : undefined"
                @update:model-value="onBoardChange"
                @update:open="onBoardSelectOpenChange"
              >
                <SelectTrigger><SelectValue placeholder="Select board" /></SelectTrigger>
                <SelectContent>
                  <SelectGroup>
                    <SelectItem v-for="b in boardOptions" :key="b.value" :value="b.value">{{
                      b.label
                    }}</SelectItem>
                  </SelectGroup>
                </SelectContent>
              </Select>
            </div>

            <div class="grid grid-cols-2 gap-3">
              <div class="space-y-1.5">
                <Label>Status</Label>
                <Select v-model="status">
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectGroup>
                      <SelectItem v-for="s in currentBoardStageLabels" :key="s" :value="s">{{
                        s
                      }}</SelectItem>
                    </SelectGroup>
                  </SelectContent>
                </Select>
              </div>
              <div class="space-y-1.5">
                <Label>Position Level</Label>
                <Select v-model="position">
                  <SelectTrigger><SelectValue placeholder="Level" /></SelectTrigger>
                  <SelectContent>
                    <SelectGroup>
                      <SelectItem v-for="p in POSITION_OPTIONS" :key="p" :value="p">{{
                        p
                      }}</SelectItem>
                    </SelectGroup>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div class="grid grid-cols-2 gap-3">
              <div class="space-y-1.5">
                <Label>Work Model</Label>
                <Select v-model="workModel">
                  <SelectTrigger><SelectValue placeholder="Work model" /></SelectTrigger>
                  <SelectContent>
                    <SelectGroup>
                      <SelectItem v-for="w in WORK_MODEL_OPTIONS" :key="w" :value="w">{{
                        w
                      }}</SelectItem>
                    </SelectGroup>
                  </SelectContent>
                </Select>
              </div>
              <div class="space-y-1.5">
                <Label>Salary Range</Label>
                <Input v-model="salaryRange" placeholder="e.g. $80k–$120k" />
              </div>
            </div>

            <div class="grid grid-cols-2 gap-3">
              <div class="space-y-1.5">
                <Label>Source Platform</Label>
                <Select v-model="sourcePlatform">
                  <SelectTrigger><SelectValue placeholder="Platform" /></SelectTrigger>
                  <SelectContent>
                    <SelectGroup>
                      <SelectItem v-for="p in PLATFORM_OPTIONS" :key="p" :value="p">{{
                        p
                      }}</SelectItem>
                    </SelectGroup>
                  </SelectContent>
                </Select>
              </div>
              <div class="space-y-1.5">
                <Label>Applied Date</Label>
                <DatePicker v-model="appliedDate" placeholder="Pick a date" />
              </div>
            </div>

            <div class="space-y-1.5">
              <Label>Job Description</Label>
              <Textarea
                v-model="description"
                placeholder="Paste the job description..."
                class="min-h-[160px] resize-none"
                rows="15"
              />
            </div>

            <div class="space-y-1.5">
              <Label>Notes</Label>
              <Textarea
                v-model="notes"
                placeholder="Personal notes..."
                class="resize-none"
                rows="3"
              />
            </div>
          </div>

          <!-- ── ATS Score pane ───────────────────────────────────────────────── -->
          <div v-show="activeTab === 'ats'" class="px-5 py-5 space-y-5">
            <!-- No job description warning -->
            <div
              v-if="!hasDescription"
              class="flex items-start gap-3 rounded-lg border border-amber-500/20 bg-amber-500/5 px-4 py-3"
            >
              <Icon name="TriangleAlert" :size="16" default-class="text-amber-400 flex-shrink-0 mt-0.5" />
              <div class="text-xs text-amber-400 leading-relaxed">
                <span class="font-medium">No job description found.</span>
                Switch to the
                <button class="underline hover:no-underline" @click="activeTab = 'details'">
                  Details tab
                </button>
                and input the JD manually to enable scoring.
              </div>
            </div>

            <!-- CV selector -->
            <div class="space-y-2">
              <div class="flex items-center justify-between">
                <Label class="text-sm">Link a CV</Label>
                <button
                  class="text-xs text-primary hover:underline flex items-center gap-1"
                  @click="router.push('/resumes')"
                >
                  <Icon name="Upload" :size="12" />
                  Upload a CV
                </button>
              </div>

              <Skeleton
                v-if="!resumesStore.loaded"
                class="h-9 rounded-md border border-input"
              />
              <template v-else-if="resumesStore.resumes.length === 0">
                <div
                  class="rounded-lg border border-dashed border-border px-4 py-5 text-center space-y-2"
                >
                  <Icon name="FileText" :size="32" default-class="mx-auto text-muted-foreground/40" />
                  <p class="text-sm text-muted-foreground">No CVs uploaded yet</p>
                </div>
              </template>
              <Select v-else v-model="selectedResumeId">
                <SelectTrigger>
                  <SelectValue placeholder="Select a CV…" />
                </SelectTrigger>
                <SelectContent>
                  <SelectGroup>
                    <SelectItem v-for="r in resumesStore.resumes" :key="r.id" :value="String(r.id)">
                      <span class="flex items-center gap-2">
                        <Icon name="FileText" :size="14" default-class="text-muted-foreground flex-shrink-0" />
                        {{ r.original_name }}
                      </span>
                    </SelectItem>
                  </SelectGroup>
                </SelectContent>
              </Select>
            </div>

            <!-- Calculate button / no-CV CTA -->
            <Button
              v-if="!(resumesStore.loaded && resumesStore.resumes.length === 0)"
              class="w-full gap-2"
              :disabled="!canScore"
              @click="calculateScore"
            >
              <Loader v-if="isScoring" :size="14" />
              <Icon v-else name="ChartColumn" :size="14" />
              {{
                isScoring
                  ? 'Analysing…'
                  : atsReport
                    ? 'Recalculate Match Score'
                    : 'Link & Calculate Match Score'
              }}
            </Button>

            <!-- ── Score result ─────────────────────────────────────────────── -->

            <template v-if="atsReport">
              <div class="border-t pt-5 space-y-5">
                <!-- Gauge + score -->
                <div class="flex items-center gap-6">
                  <AtsGauge :percentage="atsReport.score" :size="96" :stroke-width="8" :color="atsScoreColor(atsReport.score)">
                    <span class="text-2xl font-bold leading-none">{{ Math.round(atsReport.score) }}</span>
                    <span class="text-[10px] text-muted-foreground mt-0.5">/ 100</span>
                  </AtsGauge>

                  <div class="space-y-2 min-w-0">
                    <div class="flex items-center gap-2">
                      <span class="text-sm font-semibold">ATS Compatibility</span>
                      <span
                        class="text-xs font-medium px-2 py-0.5 rounded-full"
                        :class="atsTierLabel(atsReport.score).cls"
                      >
                        {{ atsTierLabel(atsReport.score).label }}
                      </span>
                    </div>
                    <p class="text-xs text-muted-foreground leading-relaxed">
                      Scored against
                      <span class="font-medium">{{ selectedResumeName || 'your CV' }}</span
                      >.
                      <button
                        class="text-primary hover:underline ml-0.5"
                        @click="calculateScore"
                        :disabled="isScoring"
                      >
                        Recalculate
                      </button>
                    </p>
                  </div>
                </div>

                <!-- Matched skills -->
                <div v-if="atsReport?.matched_skills.length" class="space-y-2">
                  <p class="text-xs font-semibold text-emerald-400 flex items-center gap-1.5">
                    <Icon name="Check" :size="14" :stroke-width="2.5" />
                    Matched skills ({{ atsReport?.matched_skills.length }})
                  </p>
                  <div class="flex flex-wrap gap-1.5">
                    <span
                      v-for="skill in atsReport.matched_skills"
                      :key="skill"
                      class="text-xs px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 font-medium"
                      >{{ skill }}</span
                    >
                  </div>
                </div>

                <!-- Matched experience -->
                <div v-if="atsReport.matched_experience?.length" class="space-y-2">
                  <p class="text-xs font-semibold text-emerald-400/70 flex items-center gap-1.5">
                    <Icon name="Check" :size="14" :stroke-width="2.5" />
                    Matched experience ({{ atsReport?.matched_experience.length }})
                  </p>
                  <ul class="space-y-1">
                    <li
                      v-for="item in atsReport.matched_experience"
                      :key="item"
                      class="text-xs text-emerald-400/70 flex items-start gap-1.5"
                    >
                      <span
                        class="mt-1 flex-shrink-0 w-1.5 h-1.5 rounded-full bg-emerald-400/50"
                      ></span>
                      {{ item }}
                    </li>
                  </ul>
                </div>

                <!-- Missing skills -->
                <div v-if="atsReport.missing_skills.length" class="space-y-2">
                  <p class="text-xs font-semibold text-red-400 flex items-center gap-1.5">
                    <Icon name="X" :size="14" :stroke-width="2.5" />
                    Missing skills ({{ atsReport.missing_skills.length }})
                  </p>
                  <div class="flex flex-wrap gap-1.5">
                    <span
                      v-for="skill in atsReport.missing_skills"
                      :key="skill"
                      class="text-xs px-2 py-0.5 rounded-full bg-red-500/10 text-red-400 font-medium"
                      >{{ skill }}</span
                    >
                  </div>
                </div>

                <!-- Experience gaps -->
                <div v-if="atsReport.experience_gaps?.length" class="space-y-2">
                  <p class="text-xs font-semibold text-amber-400 flex items-center gap-1.5">
                    <Icon name="TriangleAlert" :size="14" :stroke-width="2.5" />
                    Experience gaps ({{ atsReport.experience_gaps.length }})
                  </p>
                  <ul class="space-y-1">
                    <li
                      v-for="gap in atsReport.experience_gaps"
                      :key="gap"
                      class="text-xs text-amber-400/80 flex items-start gap-1.5"
                    >
                      <span
                        class="mt-1 flex-shrink-0 w-1.5 h-1.5 rounded-full bg-amber-400/50"
                      ></span>
                      {{ gap }}
                    </li>
                  </ul>
                </div>

                <!-- Suggestions -->
                <div v-if="atsReport.suggestions.length" class="space-y-2">
                  <p class="text-xs font-semibold text-primary flex items-center gap-1.5">
                    <Icon name="Zap" :size="14" :stroke-width="2.5" />
                    Suggestions
                  </p>
                  <ul class="space-y-2">
                    <li
                      v-for="(s, i) in atsReport.suggestions"
                      :key="i"
                      class="flex items-start gap-2 text-xs text-muted-foreground leading-relaxed"
                    >
                      <span
                        class="flex-shrink-0 w-4 h-4 rounded-full bg-primary/10 text-primary text-[10px] font-bold flex items-center justify-center mt-0.5"
                        >{{ i + 1 }}</span
                      >
                      {{ s }}
                    </li>
                  </ul>
                </div>
              </div>
            </template>

            <!-- Empty state when no report yet -->
            <template v-else-if="!isScoring">
              <div class="flex flex-col items-center justify-center py-6 text-center gap-3">
                <AtsGauge :size="80" :stroke-width="8">
                  <span class="text-xl font-bold text-muted-foreground/30">—</span>
                </AtsGauge>
                <p class="text-xs text-muted-foreground max-w-[200px] leading-relaxed">
                  Select a CV above and click
                  <span class="font-medium text-foreground">Calculate Match Score</span> to see how
                  well you match this role.
                </p>
              </div>
            </template>
          </div>

          <div v-show="activeTab === 'timeline'" class="px-5 py-5 space-y-5">
            <Skeleton v-if="jobTimelineLoading" class="h-6 rounded-md w-1/2" />
            <template v-else>
               <Timeline v-if="timelineStates?.length">
                <TimelineItem v-for="(state, index) in timelineStates" :key="`${state.label}-${index}`">
                  <template #dot>
                    <TimelineDot :class="state.color" />
                  </template>
                  <TimelineContent>
                    <TimelineTitle>{{ state.label }}</TimelineTitle>
                    <TimelineTime v-if="state.ts" :datetime="state.ts">
                      {{ formatTimelineDate(state.ts) }}
                    </TimelineTime>
                  </TimelineContent>
                </TimelineItem>
              </Timeline>

              <div v-else class="text-center text-sm text-muted-foreground">
                No timeline events yet.
              </div>
            </template>
          </div>
        </div>

        <div
          v-if="activeTab === 'details'"
          class="flex items-center justify-end gap-2 px-5 py-4 border-t"
          style="flex-shrink: 0"
        >
          <Button variant="outline" @click="$emit('update:open', false)">Cancel</Button>
          <Button :disabled="!title.trim() || !companyName.trim()" @click="handleSave"
            >Save Changes</Button
          >
        </div>
      </div>
    </SheetContent>
  </Sheet>
</template>
