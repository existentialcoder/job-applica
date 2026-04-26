<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import dataservice from '@/lib/dataservice';
import type { DashboardStats } from '@/lib/types';

const stats = ref<DashboardStats | null>(null);
const loading = ref(true);

onMounted(async () => {
  stats.value = await dataservice.getDashboardStats();
  loading.value = false;
});

// ── Funnel: only stages relevant to the pipeline (excludes Saved) ──────────
const FUNNEL_STAGES = ['Applied', 'Phone Screen', 'Interview', 'Technical', 'Offer'];
const funnelData = computed(() =>
  FUNNEL_STAGES.map(s => ({
    stage: s,
    count: stats.value?.by_stage.find(b => b.stage === s)?.count ?? 0,
  }))
);
const funnelMax = computed(() => Math.max(1, ...funnelData.value.map(d => d.count)));

// ── Weekly chart ──────────────────────────────────────────────────────────
const weeklyMax = computed(() =>
  Math.max(1, ...(stats.value?.by_week.map(w => w.count) ?? [1]))
);

function fmtWeek(iso: string) {
  const d = new Date(iso);
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

// ── Outcome donut ─────────────────────────────────────────────────────────
const OUTCOME_COLORS = ['#6366f1', '#ef4444', '#f59e0b', '#6b7280', '#10b981'];
const outcomeSegments = computed(() => {
  const o = stats.value?.overview;
  if (!o) return [];
  const total = (o.total_active + o.total_rejected + o.total_ghosted + o.total_withdrawn + o.total_offers) || 1;
  const items = [
    { label: 'Active',     value: o.total_active,    color: '#6366f1' },
    { label: 'Rejected',   value: o.total_rejected,  color: '#ef4444' },
    { label: 'Ghosted',    value: o.total_ghosted,   color: '#f59e0b' },
    { label: 'Withdrawn',  value: o.total_withdrawn, color: '#6b7280' },
    { label: 'Offers',     value: o.total_offers,    color: '#10b981' },
  ].filter(i => i.value > 0);

  let offset = 0;
  const r = 54;
  const circ = 2 * Math.PI * r;
  return items.map(item => {
    const pct = item.value / total;
    const dash = pct * circ;
    const seg = { ...item, pct: Math.round(pct * 100), dash, offset };
    offset += dash;
    return seg;
  });
});

// ── Platform max for bar scaling ──────────────────────────────────────────
const platformMax = computed(() =>
  Math.max(1, ...(stats.value?.by_platform.map(p => p.count) ?? [1]))
);

// ── Stage pill colour map ─────────────────────────────────────────────────
const STAGE_COLORS: Record<string, string> = {
  'Applied':      'bg-blue-500/15 text-blue-400',
  'Phone Screen': 'bg-amber-500/15 text-amber-400',
  'Interview':    'bg-orange-500/15 text-orange-400',
  'Technical':    'bg-purple-500/15 text-purple-400',
  'Offer':        'bg-emerald-500/15 text-emerald-400',
};
</script>

<template>
  <div class="p-6 max-w-7xl mx-auto space-y-6">

    <!-- Header -->
    <div>
      <h1 class="text-2xl font-bold tracking-tight">Dashboard</h1>
      <p class="text-sm text-muted-foreground mt-0.5">Your job search at a glance</p>
    </div>

    <!-- Loading skeleton -->
    <div v-if="loading" class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div v-for="i in 4" :key="i" class="h-28 rounded-xl bg-muted animate-pulse" />
    </div>

    <template v-else-if="stats">

      <!-- ── Stat cards row ───────────────────────────────────────────── -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">

        <!-- Applied -->
        <div class="rounded-xl border bg-card p-4 space-y-1">
          <p class="text-xs text-muted-foreground font-medium uppercase tracking-wide">Applied</p>
          <p class="text-3xl font-bold">{{ stats.overview.total_applied }}</p>
          <p class="text-xs text-muted-foreground">
            {{ stats.overview.total_saved }} saved, not yet applied
          </p>
        </div>

        <!-- Interviews -->
        <div class="rounded-xl border bg-card p-4 space-y-1">
          <p class="text-xs text-muted-foreground font-medium uppercase tracking-wide">Interviews</p>
          <p class="text-3xl font-bold text-indigo-500">{{ stats.overview.total_interviews }}</p>
          <p class="text-xs text-muted-foreground">
            {{ stats.overview.interview_rate }}% interview rate
          </p>
        </div>

        <!-- Ghosted -->
        <div class="rounded-xl border bg-card p-4 space-y-1">
          <p class="text-xs text-muted-foreground font-medium uppercase tracking-wide">Ghosted</p>
          <p class="text-3xl font-bold text-amber-500">{{ stats.overview.total_ghosted }}</p>
          <p class="text-xs text-muted-foreground">No reply in 14+ days</p>
        </div>

        <!-- Rejected -->
        <div class="rounded-xl border bg-card p-4 space-y-1">
          <p class="text-xs text-muted-foreground font-medium uppercase tracking-wide">Rejected</p>
          <p class="text-3xl font-bold text-red-500">{{ stats.overview.total_rejected }}</p>
          <p class="text-xs text-muted-foreground">
            {{ stats.overview.total_withdrawn }} withdrawn
          </p>
        </div>

      </div>

      <!-- Secondary rate strip -->
      <div class="grid grid-cols-3 gap-4">
        <div class="rounded-xl border bg-card px-4 py-3 flex items-center gap-3">
          <div class="w-2 h-8 rounded-full bg-indigo-500 flex-shrink-0" />
          <div>
            <p class="text-xs text-muted-foreground">Response Rate</p>
            <p class="text-lg font-semibold">{{ stats.overview.response_rate }}%</p>
          </div>
        </div>
        <div class="rounded-xl border bg-card px-4 py-3 flex items-center gap-3">
          <div class="w-2 h-8 rounded-full bg-emerald-500 flex-shrink-0" />
          <div>
            <p class="text-xs text-muted-foreground">Offer Rate</p>
            <p class="text-lg font-semibold">{{ stats.overview.offer_rate }}%</p>
          </div>
        </div>
        <div class="rounded-xl border bg-card px-4 py-3 flex items-center gap-3">
          <div class="w-2 h-8 rounded-full bg-amber-500 flex-shrink-0" />
          <div>
            <p class="text-xs text-muted-foreground">Stuck in Pipeline</p>
            <p class="text-lg font-semibold">{{ stats.overview.total_stuck }}</p>
          </div>
        </div>
      </div>

      <!-- ── Middle row: Funnel + Weekly ─────────────────────────────── -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">

        <!-- Application Funnel -->
        <div class="rounded-xl border bg-card p-5 space-y-4">
          <div>
            <h2 class="font-semibold text-sm">Application Funnel</h2>
            <p class="text-xs text-muted-foreground">Conversion through each stage</p>
          </div>
          <div class="space-y-3">
            <div v-for="item in funnelData" :key="item.stage" class="space-y-1">
              <div class="flex justify-between items-center">
                <span :class="['text-xs px-2 py-0.5 rounded-full font-medium', STAGE_COLORS[item.stage] ?? 'bg-muted text-muted-foreground']">
                  {{ item.stage }}
                </span>
                <span class="text-xs font-semibold tabular-nums">{{ item.count }}</span>
              </div>
              <div class="h-2 rounded-full bg-muted overflow-hidden">
                <div
                  class="h-full rounded-full transition-all duration-500"
                  :class="{
                    'bg-blue-500':    item.stage === 'Applied',
                    'bg-amber-500':   item.stage === 'Phone Screen',
                    'bg-orange-500':  item.stage === 'Interview',
                    'bg-purple-500':  item.stage === 'Technical',
                    'bg-emerald-500': item.stage === 'Offer',
                  }"
                  :style="{ width: `${(item.count / funnelMax) * 100}%` }"
                />
              </div>
              <!-- Conversion rate vs Applied -->
              <p v-if="item.stage !== 'Applied' && stats.overview.total_applied > 0" class="text-[11px] text-muted-foreground text-right">
                {{ Math.round(item.count / stats.overview.total_applied * 100) }}% of applied
              </p>
            </div>
          </div>
        </div>

        <!-- Weekly Activity -->
        <div class="rounded-xl border bg-card p-5 space-y-4">
          <div>
            <h2 class="font-semibold text-sm">Weekly Activity</h2>
            <p class="text-xs text-muted-foreground">Applications in the last 12 weeks</p>
          </div>

          <div v-if="stats.by_week.length === 0" class="flex items-center justify-center h-32 text-xs text-muted-foreground">
            No data yet
          </div>

          <div v-else class="flex items-end gap-1 h-36">
            <div
              v-for="week in stats.by_week"
              :key="week.week"
              class="group relative flex-1 flex flex-col items-center gap-1"
            >
              <!-- Tooltip -->
              <div class="absolute -top-7 left-1/2 -translate-x-1/2 hidden group-hover:block bg-popover border text-xs rounded px-1.5 py-0.5 whitespace-nowrap z-10 shadow">
                {{ fmtWeek(week.week) }}: {{ week.count }}
              </div>
              <div
                class="w-full rounded-t bg-indigo-500 hover:bg-indigo-400 transition-colors"
                :style="{ height: `${(week.count / weeklyMax) * 128}px`, minHeight: '4px' }"
              />
              <span class="text-[9px] text-muted-foreground rotate-45 origin-left translate-x-1 hidden sm:block">
                {{ fmtWeek(week.week) }}
              </span>
            </div>
          </div>
        </div>

      </div>

      <!-- ── Bottom row: Outcome donut + Platform + Companies ───────── -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">

        <!-- Outcome Breakdown -->
        <div class="rounded-xl border bg-card p-5 space-y-4">
          <div>
            <h2 class="font-semibold text-sm">Outcome Breakdown</h2>
            <p class="text-xs text-muted-foreground">Where applications ended up</p>
          </div>

          <div v-if="outcomeSegments.length === 0" class="flex items-center justify-center h-32 text-xs text-muted-foreground">
            No outcome data yet
          </div>

          <div v-else class="flex flex-col items-center gap-4">
            <!-- SVG Donut -->
            <svg viewBox="0 0 128 128" class="w-32 h-32 -rotate-90">
              <circle cx="64" cy="64" r="54" fill="none" stroke="currentColor" stroke-width="16" class="text-muted/30" />
              <circle
                v-for="seg in outcomeSegments"
                :key="seg.label"
                cx="64" cy="64" r="54"
                fill="none"
                :stroke="seg.color"
                stroke-width="16"
                :stroke-dasharray="`${seg.dash} ${2 * Math.PI * 54 - seg.dash}`"
                :stroke-dashoffset="-seg.offset"
              />
            </svg>
            <!-- Legend -->
            <div class="w-full space-y-1.5">
              <div v-for="seg in outcomeSegments" :key="seg.label" class="flex items-center justify-between">
                <div class="flex items-center gap-2">
                  <div class="w-2.5 h-2.5 rounded-full flex-shrink-0" :style="{ background: seg.color }" />
                  <span class="text-xs">{{ seg.label }}</span>
                </div>
                <span class="text-xs font-semibold tabular-nums">{{ seg.pct }}%</span>
              </div>
            </div>
          </div>
        </div>

        <!-- By Platform -->
        <div class="rounded-xl border bg-card p-5 space-y-4">
          <div>
            <h2 class="font-semibold text-sm">By Platform</h2>
            <p class="text-xs text-muted-foreground">Where you found the roles</p>
          </div>

          <div v-if="stats.by_platform.length === 0" class="flex items-center justify-center h-32 text-xs text-muted-foreground">
            No platform data yet
          </div>

          <div v-else class="space-y-3">
            <div v-for="p in stats.by_platform" :key="p.platform" class="space-y-1">
              <div class="flex justify-between text-xs">
                <span class="font-medium">{{ p.platform }}</span>
                <span class="text-muted-foreground tabular-nums">{{ p.count }}</span>
              </div>
              <div class="h-1.5 rounded-full bg-muted overflow-hidden">
                <div
                  class="h-full rounded-full bg-indigo-500 transition-all duration-500"
                  :style="{ width: `${(p.count / platformMax) * 100}%` }"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- Top Companies -->
        <div class="rounded-xl border bg-card p-5 space-y-4">
          <div>
            <h2 class="font-semibold text-sm">Top Companies</h2>
            <p class="text-xs text-muted-foreground">Most applications sent to</p>
          </div>

          <div v-if="stats.top_companies.length === 0" class="flex items-center justify-center h-32 text-xs text-muted-foreground">
            No company data yet
          </div>

          <div v-else class="space-y-2">
            <div
              v-for="(c, i) in stats.top_companies"
              :key="c.company"
              class="flex items-center gap-3"
            >
              <span class="text-xs text-muted-foreground w-4 text-right tabular-nums">{{ i + 1 }}</span>
              <div class="flex-1 min-w-0">
                <div class="flex justify-between items-center">
                  <span class="text-xs font-medium truncate">{{ c.company }}</span>
                  <span class="text-xs text-muted-foreground tabular-nums ml-2">{{ c.count }}</span>
                </div>
                <div class="mt-1 h-1 rounded-full bg-muted overflow-hidden">
                  <div
                    class="h-full rounded-full bg-violet-500 transition-all duration-500"
                    :style="{ width: `${(c.count / (stats.top_companies[0]?.count || 1)) * 100}%` }"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

      </div>

    </template>

    <!-- Empty state -->
    <div v-else class="flex flex-col items-center justify-center h-64 gap-3 text-muted-foreground">
      <p class="text-sm">Could not load dashboard data.</p>
    </div>

  </div>
</template>
