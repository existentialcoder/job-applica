<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import type { JobData, JobCreatePayload, ATSReport, ResumeData } from '@/lib/types';
import { Sheet, SheetContent, SheetTitle } from '@/components/ui/sheet';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select, SelectContent, SelectGroup, SelectItem, SelectTrigger, SelectValue,
} from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import dataservice from '@/lib/dataservice';

const router = useRouter();

const props = defineProps<{
  open: boolean
  job?: JobData | null
  statusOptions?: string[]
  initialTab?: 'details' | 'ats'
}>();

const emit = defineEmits<{
  (e: 'update:open', val: boolean): void
  (e: 'save', id: number, payload: JobCreatePayload): void
  (e: 'tab-change', tab: 'details' | 'ats'): void
  (e: 'score-updated', jobId: number, update: { ats_score: number; ats_report: ATSReport }): void
}>();

const STATUS_OPTIONS = ['Saved', 'Applied', 'Phone Screen', 'Interview', 'Technical', 'Offer', 'Rejected', 'Withdrawn'];
const POSITION_OPTIONS = ['Intern', 'Junior', 'Mid', 'Senior', 'Lead', 'Manager'];
const WORK_MODEL_OPTIONS = ['On-site', 'Remote', 'Hybrid'];
const PLATFORM_OPTIONS = ['LinkedIn', 'Indeed', 'Glassdoor', 'Monster', 'ZipRecruiter', 'Jobscan', 'Other'];

const activeTab = ref<'details' | 'ats'>('details');

// ── Details fields ────────────────────────────────────────────────────────────
const title = ref('');
const companyName = ref('');
const location = ref('');
const status = ref('');
const position = ref('');
const workModel = ref('');
const salaryRange = ref('');
const sourcePlatform = ref('');
const sourceUrl = ref('');
const appliedDate = ref('');
const description = ref('');
const notes = ref('');

// ── Inline URL edit ──────────────────────────────────────────────────────────
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

// ── ATS state ─────────────────────────────────────────────────────────────────
const resumes = ref<ResumeData[]>([]);
const resumesLoaded = ref(false);
const selectedResumeId = ref<string>('');
const atsReport = ref<ATSReport | null>(null);
const isScoring = ref(false);
const scoringError = ref('');

const selectedResumeName = computed(() => {
  if (!selectedResumeId.value) return '';
  const r = resumes.value.find(r => String(r.id) === selectedResumeId.value);
  return r?.original_name ?? '';
});

const hasDescription = computed(() => !!description.value.trim());
const hasLinkedCv = computed(() => !!selectedResumeId.value);
const canScore = computed(() => hasDescription.value && hasLinkedCv.value && !isScoring.value);

function atsScoreColor(score: number) {
  if (score >= 85) return '#22c55e';   // green
  if (score >= 70) return '#6366f1';   // indigo
  if (score >= 50) return '#f59e0b';   // amber
  return '#ef4444';                     // red
}

function atsTierLabel(score: number) {
  if (score >= 85) return { label: 'Excellent', cls: 'bg-emerald-500/10 text-emerald-400' };
  if (score >= 70) return { label: 'Good', cls: 'bg-indigo-500/10 text-indigo-400' };
  if (score >= 50) return { label: 'Fair', cls: 'bg-amber-500/10 text-amber-400' };
  return { label: 'Low', cls: 'bg-red-500/10 text-red-400' };
}

// SVG gauge helpers — full circle circumference for r=42: 2π*42 ≈ 263.9
const CIRC = 263.9;
function gaugeOffset(score: number) {
  return CIRC - (score / 100) * CIRC;
}

async function loadResumes() {
  if (resumesLoaded.value) return;
  resumes.value = await dataservice.getResumes();
  resumesLoaded.value = true;
  // Pre-select the linked resume if set, else default
  if (props.job?.ats_resume_id) {
    selectedResumeId.value = String(props.job.ats_resume_id);
  } else {
    const def = resumes.value.find(r => (r as any).is_default);
    if (def) selectedResumeId.value = String(def.id);
    else if (resumes.value.length) selectedResumeId.value = String(resumes.value[0].id);
  }
}

async function calculateScore() {
  if (!props.job || !canScore.value) return;
  isScoring.value = true;
  scoringError.value = '';
  try {
    const report = await dataservice.calculateAtsScore(
      props.job.id,
      selectedResumeId.value ? Number(selectedResumeId.value) : null,
    );
    atsReport.value = report;
    emit('score-updated', props.job.id, { ats_score: report.score, ats_report: report });
  } catch (err: any) {
    scoringError.value = err.message ?? 'Scoring failed';
  } finally {
    isScoring.value = false;
  }
}

watch(activeTab, (tab) => {
  emit('tab-change', tab);
  if (tab === 'ats') loadResumes();
});

watch(() => props.open, (open) => {
  if (!open) {
    isEditingUrl.value = false;
    atsReport.value = null;
    scoringError.value = '';
    resumesLoaded.value = false;
    selectedResumeId.value = '';
    return;
  }
  activeTab.value = props.initialTab ?? 'details';
  const job = props.job;
  if (!job) return;
  title.value = job.title || '';
  companyName.value = job.company?.name || '';
  location.value = job.location
    ? [job.location.city, job.location.state, job.location.country].filter(Boolean).join(', ')
    : '';
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

  if (activeTab.value === 'ats') loadResumes();
});

function handleSave() {
  if (!props.job || !title.value.trim()) return;
  emit('save', props.job.id, {
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
  });
}

const statusVariantMap: Record<string, string> = {
  Saved: 'secondary', Applied: 'default',
  'Phone Screen': 'warning', Interview: 'warning', Technical: 'warning',
  Offer: 'success', Rejected: 'danger', Withdrawn: 'outline',
};
</script>

<template>
  <Sheet :open="open" @update:open="$emit('update:open', $event)">
    <SheetContent side="right" class="!w-[40vw] !max-w-[40vw] !p-0 !gap-0">
      <div style="display:flex; flex-direction:column; height:100vh; overflow:hidden;">

        <!-- ── Header ────────────────────────────────────────────────────────── -->
        <div class="flex items-start gap-3 px-5 pt-5 pb-4 border-b" style="flex-shrink:0;">
          <div class="flex-1 min-w-0">
            <SheetTitle class="text-base font-semibold leading-snug truncate">
              {{ job?.title || 'Job Detail' }}
            </SheetTitle>

            <div class="flex items-center gap-2 mt-0.5 flex-wrap">
              <span v-if="job?.company" class="text-sm text-muted-foreground">{{ job.company.name }}</span>
              <Badge
                v-if="job?.status"
                :variant="(statusVariantMap[job.status] as any) || 'outline'"
                class="text-xs"
              >{{ job.status }}</Badge>
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
                <button class="flex-shrink-0 text-green-500 hover:text-green-400 transition-colors p-0.5" title="Confirm" @click="confirmUrl">
                  <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
                  </svg>
                </button>
                <button class="flex-shrink-0 text-muted-foreground hover:text-foreground transition-colors p-0.5" title="Cancel" @click="cancelUrl">
                  <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </template>

              <template v-else-if="sourceUrl">
                <a :href="sourceUrl" target="_blank" rel="noopener" class="flex items-center gap-1 text-xs text-indigo-400 hover:underline flex-shrink-0" :title="sourceUrl">
                  <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                  Go to job posting
                </a>
                <button class="flex-shrink-0 text-muted-foreground hover:text-foreground transition-colors p-0.5" title="Edit link" @click="startEditUrl">
                  <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                  </svg>
                </button>
              </template>

              <button v-else class="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors" @click="startEditUrl">
                <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                </svg>
                Add link
              </button>
            </div>
          </div>

          <button
            class="flex-shrink-0 p-1.5 rounded-md text-muted-foreground hover:text-foreground hover:bg-muted transition-colors mt-0.5"
            aria-label="Close"
            @click="$emit('update:open', false)"
          >
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- ── Tab bar ───────────────────────────────────────────────────────── -->
        <div class="px-5 pt-3 pb-3 border-b" style="flex-shrink:0;">
          <Tabs v-model="activeTab">
            <TabsList>
              <TabsTrigger value="details">Details</TabsTrigger>
              <TabsTrigger value="ats">
                ATS Score
                <span
                  v-if="job?.ats_score != null"
                  class="ml-1.5 text-[10px] font-bold px-1.5 py-0.5 rounded-full"
                  :class="atsTierLabel(job.ats_score).cls"
                >{{ Math.round(job.ats_score) }}</span>
              </TabsTrigger>
            </TabsList>
          </Tabs>
        </div>

        <!-- ── Scrollable content ────────────────────────────────────────────── -->
        <div style="flex:1; min-height:0; overflow-y:auto;">

          <!-- ── Details pane ────────────────────────────────────────────────── -->
          <div v-show="activeTab === 'details'" class="px-5 py-4 space-y-4">
            <div class="space-y-1.5">
              <Label>Job Title <span class="text-destructive">*</span></Label>
              <Input v-model="title" placeholder="e.g. Senior Software Engineer" />
            </div>

            <div class="grid grid-cols-2 gap-3">
              <div class="space-y-1.5">
                <Label>Company</Label>
                <Input v-model="companyName" placeholder="e.g. Acme Corp" />
              </div>
              <div class="space-y-1.5">
                <Label>Location</Label>
                <Input v-model="location" placeholder="e.g. New York, NY" />
              </div>
            </div>

            <div class="grid grid-cols-2 gap-3">
              <div class="space-y-1.5">
                <Label>Status</Label>
                <Select v-model="status">
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectGroup>
                      <SelectItem v-for="s in (statusOptions ?? STATUS_OPTIONS)" :key="s" :value="s">{{ s }}</SelectItem>
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
                      <SelectItem v-for="p in POSITION_OPTIONS" :key="p" :value="p">{{ p }}</SelectItem>
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
                      <SelectItem v-for="w in WORK_MODEL_OPTIONS" :key="w" :value="w">{{ w }}</SelectItem>
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
                      <SelectItem v-for="p in PLATFORM_OPTIONS" :key="p" :value="p">{{ p }}</SelectItem>
                    </SelectGroup>
                  </SelectContent>
                </Select>
              </div>
              <div class="space-y-1.5">
                <Label>Applied Date</Label>
                <Input v-model="appliedDate" type="date" />
              </div>
            </div>

            <div class="space-y-1.5">
              <Label>Job Description</Label>
              <Textarea v-model="description" placeholder="Paste the job description..." class="min-h-[160px] resize-none" rows="7" />
            </div>

            <div class="space-y-1.5">
              <Label>Notes</Label>
              <Textarea v-model="notes" placeholder="Personal notes..." class="resize-none" rows="3" />
            </div>
          </div>

          <!-- ── ATS Score pane ───────────────────────────────────────────────── -->
          <div v-show="activeTab === 'ats'" class="px-5 py-5 space-y-5">

            <!-- No job description warning -->
            <div
              v-if="!hasDescription"
              class="flex items-start gap-3 rounded-lg border border-amber-500/20 bg-amber-500/5 px-4 py-3"
            >
              <svg class="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <div class="text-xs text-amber-400 leading-relaxed">
                <span class="font-medium">No job description found.</span>
                Switch to the <button class="underline hover:no-underline" @click="activeTab = 'details'">Details tab</button> and paste the JD first — ATS scoring needs the job description to compare against your CV.
              </div>
            </div>

            <!-- CV selector -->
            <div class="space-y-2">
              <div class="flex items-center justify-between">
                <Label class="text-sm">Link a CV</Label>
                <button
                  class="text-xs text-indigo-400 hover:underline flex items-center gap-1"
                  @click="router.push('/settings?tab=resumes')"
                >
                  <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                  </svg>
                  Upload a CV
                </button>
              </div>

              <div v-if="!resumesLoaded" class="h-9 rounded-md border border-input bg-muted/40 animate-pulse" />
              <template v-else-if="resumes.length === 0">
                <div class="rounded-lg border border-dashed border-border px-4 py-5 text-center space-y-2">
                  <svg class="w-8 h-8 mx-auto text-muted-foreground/40" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <p class="text-sm text-muted-foreground">No CVs uploaded yet</p>
                  <Button size="sm" variant="outline" @click="router.push('/settings?tab=resumes')">
                    Upload your CV
                  </Button>
                </div>
              </template>
              <Select v-else v-model="selectedResumeId">
                <SelectTrigger>
                  <SelectValue placeholder="Select a CV…" />
                </SelectTrigger>
                <SelectContent>
                  <SelectGroup>
                    <SelectItem v-for="r in resumes" :key="r.id" :value="String(r.id)">
                      <span class="flex items-center gap-2">
                        <svg class="w-3.5 h-3.5 text-muted-foreground flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                          <path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                        {{ r.original_name }}
                      </span>
                    </SelectItem>
                  </SelectGroup>
                </SelectContent>
              </Select>
            </div>

            <!-- Calculate button / no-CV CTA -->
            <template v-if="resumesLoaded && resumes.length === 0">
              <Button class="w-full gap-2" variant="outline" @click="router.push('/settings?tab=resumes')">
                <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                </svg>
                Upload your CV to score this job
              </Button>
            </template>
            <Button
              v-else
              class="w-full gap-2"
              :disabled="!canScore"
              @click="calculateScore"
            >
              <svg v-if="isScoring" class="w-3.5 h-3.5 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
              </svg>
              <svg v-else class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
              {{ isScoring ? 'Analysing…' : atsReport ? 'Recalculate ATS Score' : 'Calculate ATS Score' }}
            </Button>

            <p v-if="scoringError" class="text-xs text-destructive">{{ scoringError }}</p>

            <!-- ── Score result ─────────────────────────────────────────────── -->
            <template v-if="atsReport">
              <div class="border-t pt-5 space-y-5">

                <!-- Gauge + score -->
                <div class="flex items-center gap-6">
                  <div class="relative w-24 h-24 flex-shrink-0">
                    <svg class="w-24 h-24 -rotate-90" viewBox="0 0 100 100">
                      <circle cx="50" cy="50" r="42" fill="none" stroke="currentColor" stroke-width="8" class="text-muted/30" />
                      <circle
                        cx="50" cy="50" r="42"
                        fill="none"
                        :stroke="atsScoreColor(atsReport.score)"
                        stroke-width="8"
                        stroke-linecap="round"
                        :stroke-dasharray="CIRC"
                        :stroke-dashoffset="gaugeOffset(atsReport.score)"
                        style="transition: stroke-dashoffset 0.8s ease"
                      />
                    </svg>
                    <div class="absolute inset-0 flex flex-col items-center justify-center">
                      <span class="text-2xl font-bold leading-none">{{ Math.round(atsReport.score) }}</span>
                      <span class="text-[10px] text-muted-foreground mt-0.5">/ 100</span>
                    </div>
                  </div>

                  <div class="space-y-2 min-w-0">
                    <div class="flex items-center gap-2">
                      <span class="text-sm font-semibold">ATS Compatibility</span>
                      <span class="text-xs font-medium px-2 py-0.5 rounded-full" :class="atsTierLabel(atsReport.score).cls">
                        {{ atsTierLabel(atsReport.score).label }}
                      </span>
                    </div>
                    <p class="text-xs text-muted-foreground leading-relaxed">
                      Scored against <span class="font-medium">{{ selectedResumeName || 'your CV' }}</span>.
                      <button class="text-indigo-400 hover:underline ml-0.5" @click="calculateScore" :disabled="isScoring">Recalculate</button>
                    </p>
                  </div>
                </div>

                <!-- Matched skills -->
                <div v-if="atsReport.matched_skills.length" class="space-y-2">
                  <p class="text-xs font-semibold text-emerald-400 flex items-center gap-1.5">
                    <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
                    </svg>
                    Matched skills ({{ atsReport.matched_skills.length }})
                  </p>
                  <div class="flex flex-wrap gap-1.5">
                    <span
                      v-for="skill in atsReport.matched_skills"
                      :key="skill"
                      class="text-xs px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 font-medium"
                    >{{ skill }}</span>
                  </div>
                </div>

                <!-- Matched experience -->
                <div v-if="atsReport.matched_experience?.length" class="space-y-2">
                  <p class="text-xs font-semibold text-emerald-400/70 flex items-center gap-1.5">
                    <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
                    </svg>
                    Matched experience ({{ atsReport.matched_experience.length }})
                  </p>
                  <ul class="space-y-1">
                    <li
                      v-for="item in atsReport.matched_experience"
                      :key="item"
                      class="text-xs text-emerald-400/70 flex items-start gap-1.5"
                    >
                      <span class="mt-1 flex-shrink-0 w-1.5 h-1.5 rounded-full bg-emerald-400/50"></span>
                      {{ item }}
                    </li>
                  </ul>
                </div>

                <!-- Missing skills -->
                <div v-if="atsReport.missing_skills.length" class="space-y-2">
                  <p class="text-xs font-semibold text-red-400 flex items-center gap-1.5">
                    <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                    Missing skills ({{ atsReport.missing_skills.length }})
                  </p>
                  <div class="flex flex-wrap gap-1.5">
                    <span
                      v-for="skill in atsReport.missing_skills"
                      :key="skill"
                      class="text-xs px-2 py-0.5 rounded-full bg-red-500/10 text-red-400 font-medium"
                    >{{ skill }}</span>
                  </div>
                </div>

                <!-- Experience gaps -->
                <div v-if="atsReport.experience_gaps?.length" class="space-y-2">
                  <p class="text-xs font-semibold text-amber-400 flex items-center gap-1.5">
                    <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v4m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
                    </svg>
                    Experience gaps ({{ atsReport.experience_gaps.length }})
                  </p>
                  <ul class="space-y-1">
                    <li
                      v-for="gap in atsReport.experience_gaps"
                      :key="gap"
                      class="text-xs text-amber-400/80 flex items-start gap-1.5"
                    >
                      <span class="mt-1 flex-shrink-0 w-1.5 h-1.5 rounded-full bg-amber-400/50"></span>
                      {{ gap }}
                    </li>
                  </ul>
                </div>

                <!-- Suggestions -->
                <div v-if="atsReport.suggestions.length" class="space-y-2">
                  <p class="text-xs font-semibold text-indigo-400 flex items-center gap-1.5">
                    <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                    Suggestions
                  </p>
                  <ul class="space-y-2">
                    <li
                      v-for="(s, i) in atsReport.suggestions"
                      :key="i"
                      class="flex items-start gap-2 text-xs text-muted-foreground leading-relaxed"
                    >
                      <span class="flex-shrink-0 w-4 h-4 rounded-full bg-indigo-500/10 text-indigo-400 text-[10px] font-bold flex items-center justify-center mt-0.5">{{ i + 1 }}</span>
                      {{ s }}
                    </li>
                  </ul>
                </div>

              </div>
            </template>

            <!-- Empty state when no report yet -->
            <template v-else-if="!isScoring">
              <div class="flex flex-col items-center justify-center py-6 text-center gap-3">
                <div class="relative w-20 h-20">
                  <svg class="w-20 h-20 -rotate-90" viewBox="0 0 100 100">
                    <circle cx="50" cy="50" r="42" fill="none" stroke="currentColor" stroke-width="8" class="text-muted/30" />
                  </svg>
                  <div class="absolute inset-0 flex items-center justify-center">
                    <span class="text-xl font-bold text-muted-foreground/30">—</span>
                  </div>
                </div>
                <p class="text-xs text-muted-foreground max-w-[200px] leading-relaxed">
                  Select a CV above and click <span class="font-medium text-foreground">Calculate ATS Score</span> to see how well you match this role.
                </p>
              </div>
            </template>

          </div>
        </div>

        <!-- ── Footer ────────────────────────────────────────────────────────── -->
        <div
          v-if="activeTab === 'details'"
          class="flex items-center justify-end gap-2 px-5 py-4 border-t"
          style="flex-shrink:0;"
        >
          <Button variant="outline" @click="$emit('update:open', false)">Cancel</Button>
          <Button :disabled="!title.trim()" @click="handleSave">Save Changes</Button>
        </div>

      </div>
    </SheetContent>
  </Sheet>
</template>
