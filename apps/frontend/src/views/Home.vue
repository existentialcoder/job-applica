<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import { LayoutDashboard } from 'lucide-vue-next';
import dataservice from '@/lib/dataservice';
import type { DashboardStats, BoardData } from '@/lib/types';
import DashboardWidget from '@/components/core/DashboardWidget.vue';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Button } from '@/components/ui/button';

const stats   = ref<DashboardStats | null>(null);
const boards  = ref<BoardData[]>([]);
const boardId = ref<number | null>(null);
const loading = ref(true);

// ── Widget visibility ─────────────────────────────────────────────────────────
const WIDGET_DEFS = [
  { id: 'stat-cards', label: 'Summary Cards',       description: 'Applied, Interviews, Ghosted, Rejected' },
  { id: 'rate-strip', label: 'Rate Metrics',         description: 'Response rate, offer rate, stuck count' },
  { id: 'funnel',     label: 'Application Funnel',   description: 'Conversion through each stage' },
  { id: 'weekly',     label: 'Weekly Activity',      description: 'Applications over the last 12 weeks' },
  { id: 'outcome',    label: 'Outcome Breakdown',    description: 'Donut chart of where applications ended up' },
  { id: 'platform',   label: 'By Platform',          description: 'Where you found the roles' },
  { id: 'companies',  label: 'Top Companies',        description: 'Most applications sent to' },
] as const;

type WidgetId = typeof WIDGET_DEFS[number]['id'];

const hiddenWidgets = ref<WidgetId[]>([]);

function isVisible(id: WidgetId) { return !hiddenWidgets.value.includes(id); }

async function setHidden(ids: WidgetId[]) {
  hiddenWidgets.value = ids;
  await dataservice.updateSettings({ hidden_widgets: ids });
}

function removeWidget(id: WidgetId) {
  setHidden([...hiddenWidgets.value, id]);
}

function toggleWidget(id: WidgetId) {
  if (hiddenWidgets.value.includes(id)) {
    setHidden(hiddenWidgets.value.filter(w => w !== id));
  } else {
    setHidden([...hiddenWidgets.value, id]);
  }
}

const hiddenCount = computed(() => hiddenWidgets.value.length);

// ── Data ──────────────────────────────────────────────────────────────────────
async function fetchStats() {
  loading.value = true;
  stats.value = await dataservice.getDashboardStats(boardId.value ?? undefined);
  loading.value = false;
}

onMounted(async () => {
  const [, boardList, settings] = await Promise.all([
    fetchStats(),
    dataservice.getBoards(),
    dataservice.getSettings(),
  ]);
  boards.value = boardList;
  hiddenWidgets.value = (settings.hidden_widgets as WidgetId[] | undefined) ?? [];
});

watch(boardId, fetchStats);

// ── Funnel ────────────────────────────────────────────────────────────────────
const TERMINAL_KEYS = new Set(['Saved', 'Rejected', 'Withdrawn']);
const funnelData = computed(() => {
  if (!stats.value) return [];
  return stats.value.stages
    .filter(s => !TERMINAL_KEYS.has(s.key))
    .map(s => ({
      key:   s.key,
      label: s.label,
      color: s.color,
      count: stats.value!.by_stage.find(b => b.stage === s.key)?.count ?? 0,
    }));
});
const funnelMax = computed(() => Math.max(1, ...funnelData.value.map(d => d.count)));

// ── Weekly ────────────────────────────────────────────────────────────────────
const weeklyMax = computed(() =>
  Math.max(1, ...(stats.value?.by_week.map(w => w.count) ?? [1]))
);

function fmtWeek(iso: string) {
  const d = new Date(iso);
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

// ── Outcome donut ─────────────────────────────────────────────────────────────
const outcomeSegments = computed(() => {
  const o = stats.value?.overview;
  if (!o) return [];
  const total = (o.total_active + o.total_rejected + o.total_ghosted + o.total_withdrawn + o.total_offers) || 1;
  const items = [
    { label: 'Active',    value: o.total_active,    color: '#6366f1' },
    { label: 'Rejected',  value: o.total_rejected,  color: '#ef4444' },
    { label: 'Ghosted',   value: o.total_ghosted,   color: '#f59e0b' },
    { label: 'Withdrawn', value: o.total_withdrawn, color: '#6b7280' },
    { label: 'Offers',    value: o.total_offers,    color: '#10b981' },
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

// ── Platform ──────────────────────────────────────────────────────────────────
const platformMax = computed(() =>
  Math.max(1, ...(stats.value?.by_platform.map(p => p.count) ?? [1]))
);

// ── Helpers ───────────────────────────────────────────────────────────────────
function stagePillClass(tailwindColor: string): string {
  const match = tailwindColor.match(/^bg-(\w+-\d+)$/) ?? tailwindColor.match(/^(\w+-\d+)$/);
  const base = match?.[1] ?? 'indigo-500';
  return `bg-${base}/15 text-${base.replace(/\d+$/, '400')}`;
}
</script>

<template>
  <div class="p-6 max-w-7xl mx-auto space-y-6">

    <!-- Header -->
    <div class="flex items-start justify-between gap-4 flex-wrap">
      <div>
        <h1 class="text-2xl font-bold tracking-tight">Dashboard</h1>
        <p class="text-sm text-muted-foreground mt-0.5">Your job search at a glance</p>
      </div>

      <div class="flex items-center gap-2">
        <!-- Customize widgets -->
        <Popover>
          <PopoverTrigger as-child>
            <Button variant="outline" class="h-9 gap-2 text-sm">
              <LayoutDashboard class="w-4 h-4" />
              Widgets
              <span v-if="hiddenCount" class="ml-0.5 text-xs bg-indigo-500/20 text-indigo-400 rounded-full px-1.5 py-0.5 font-medium">
                {{ hiddenCount }} off
              </span>
            </Button>
          </PopoverTrigger>
          <PopoverContent class="w-72 p-3" align="end">
            <p class="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2 px-1">Visible widgets</p>
            <div class="space-y-0.5">
              <button
                v-for="w in WIDGET_DEFS"
                :key="w.id"
                @click="toggleWidget(w.id)"
                class="w-full flex items-center gap-3 px-2 py-2 rounded-lg hover:bg-muted transition-colors text-left"
              >
                <div
                  class="w-4 h-4 rounded border flex-shrink-0 flex items-center justify-center transition-colors"
                  :class="isVisible(w.id) ? 'bg-indigo-500 border-indigo-500' : 'bg-transparent border-border'"
                >
                  <svg v-if="isVisible(w.id)" class="w-2.5 h-2.5 text-white" viewBox="0 0 10 10" fill="none">
                    <path d="M2 5l2.5 2.5L8 3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                </div>
                <div class="min-w-0">
                  <p class="text-sm font-medium leading-tight">{{ w.label }}</p>
                  <p class="text-xs text-muted-foreground truncate">{{ w.description }}</p>
                </div>
              </button>
            </div>
          </PopoverContent>
        </Popover>

        <!-- Board filter -->
        <select
          v-model="boardId"
          class="h-9 rounded-lg border bg-card px-3 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
        >
          <option :value="null">All boards</option>
          <option v-for="b in boards" :key="b.id" :value="b.id">{{ b.name }}</option>
        </select>
      </div>
    </div>

    <!-- Loading skeleton -->
    <div v-if="loading" class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div v-for="i in 4" :key="i" class="h-28 rounded-xl bg-muted animate-pulse" />
    </div>

    <template v-else-if="stats">

      <!-- ── Stat cards ──────────────────────────────────────────────────── -->
      <div v-if="isVisible('stat-cards')" class="rounded-xl border bg-card p-4">
        <div class="flex items-center justify-between mb-3">
          <p class="text-xs font-semibold text-muted-foreground uppercase tracking-wide">Summary</p>
          <button
            @click="removeWidget('stat-cards')"
            class="p-1 rounded hover:bg-muted transition-colors text-muted-foreground hover:text-destructive"
            title="Remove widget"
          >
            <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div class="space-y-1">
            <p class="text-xs text-muted-foreground font-medium uppercase tracking-wide">Applied</p>
            <p class="text-3xl font-bold">{{ stats.overview.total_applied }}</p>
            <p class="text-xs text-muted-foreground">{{ stats.overview.total_saved }} saved, not yet applied</p>
          </div>
          <div class="space-y-1">
            <p class="text-xs text-muted-foreground font-medium uppercase tracking-wide">Interviews</p>
            <p class="text-3xl font-bold text-indigo-500">{{ stats.overview.total_interviews }}</p>
            <p class="text-xs text-muted-foreground">{{ stats.overview.interview_rate }}% interview rate</p>
          </div>
          <div class="space-y-1">
            <p class="text-xs text-muted-foreground font-medium uppercase tracking-wide">Ghosted</p>
            <p class="text-3xl font-bold text-amber-500">{{ stats.overview.total_ghosted }}</p>
            <p class="text-xs text-muted-foreground">No reply in 14+ days</p>
          </div>
          <div class="space-y-1">
            <p class="text-xs text-muted-foreground font-medium uppercase tracking-wide">Rejected</p>
            <p class="text-3xl font-bold text-red-500">{{ stats.overview.total_rejected }}</p>
            <p class="text-xs text-muted-foreground">{{ stats.overview.total_withdrawn }} withdrawn</p>
          </div>
        </div>
      </div>

      <!-- ── Rate strip ──────────────────────────────────────────────────── -->
      <div v-if="isVisible('rate-strip')" class="rounded-xl border bg-card p-4">
        <div class="flex items-center justify-between mb-3">
          <p class="text-xs font-semibold text-muted-foreground uppercase tracking-wide">Rate Metrics</p>
          <button
            @click="removeWidget('rate-strip')"
            class="p-1 rounded hover:bg-muted transition-colors text-muted-foreground hover:text-destructive"
            title="Remove widget"
          >
            <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
        <div class="grid grid-cols-3 gap-4">
          <div class="flex items-center gap-3">
            <div class="w-2 h-8 rounded-full bg-indigo-500 flex-shrink-0" />
            <div>
              <p class="text-xs text-muted-foreground">Response Rate</p>
              <p class="text-lg font-semibold">{{ stats.overview.response_rate }}%</p>
            </div>
          </div>
          <div class="flex items-center gap-3">
            <div class="w-2 h-8 rounded-full bg-emerald-500 flex-shrink-0" />
            <div>
              <p class="text-xs text-muted-foreground">Offer Rate</p>
              <p class="text-lg font-semibold">{{ stats.overview.offer_rate }}%</p>
            </div>
          </div>
          <div class="flex items-center gap-3">
            <div class="w-2 h-8 rounded-full bg-amber-500 flex-shrink-0" />
            <div>
              <p class="text-xs text-muted-foreground">Stuck in Pipeline</p>
              <p class="text-lg font-semibold">{{ stats.overview.total_stuck }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- ── Funnel + Weekly ─────────────────────────────────────────────── -->
      <div
        v-if="isVisible('funnel') || isVisible('weekly')"
        class="grid gap-4"
        :class="isVisible('funnel') && isVisible('weekly') ? 'md:grid-cols-2' : 'grid-cols-1'"
      >

        <!-- Application Funnel -->
        <DashboardWidget
          v-if="isVisible('funnel')"
          title="Application Funnel"
          subtitle="Conversion through each stage"
          @remove="removeWidget('funnel')"
        >
          <template #default="{ expanded }">
            <div class="space-y-3" :class="expanded ? 'max-h-96 overflow-y-auto pr-1' : ''">
              <div v-for="(item, i) in funnelData" :key="item.key" class="space-y-1">
                <div class="flex justify-between items-center">
                  <span :class="['text-xs px-2 py-0.5 rounded-full font-medium', stagePillClass(item.color)]">
                    {{ item.label }}
                  </span>
                  <span class="text-xs font-semibold tabular-nums">{{ item.count }}</span>
                </div>
                <div class="h-2 rounded-full bg-muted overflow-hidden">
                  <div
                    class="h-full rounded-full transition-all duration-500"
                    :class="item.color"
                    :style="{ width: `${(item.count / funnelMax) * 100}%` }"
                  />
                </div>
                <p v-if="i > 0 && funnelData[0].count > 0" class="text-[11px] text-muted-foreground text-right">
                  {{ Math.round(item.count / funnelData[0].count * 100) }}% of {{ funnelData[0].label.toLowerCase() }}
                </p>
              </div>
              <p v-if="funnelData.length === 0" class="text-xs text-muted-foreground text-center py-8">No stage data yet</p>
            </div>
          </template>
        </DashboardWidget>

        <!-- Weekly Activity -->
        <DashboardWidget
          v-if="isVisible('weekly')"
          title="Weekly Activity"
          subtitle="Applications in the last 12 weeks"
          @remove="removeWidget('weekly')"
        >
          <template #default="{ expanded }">
            <div v-if="stats.by_week.length === 0" class="flex items-center justify-center h-32 text-xs text-muted-foreground">
              No data yet
            </div>
            <div v-else class="flex items-end gap-1" :class="expanded ? 'h-64' : 'h-36'">
              <div
                v-for="week in stats.by_week"
                :key="week.week"
                class="group relative flex-1 flex flex-col items-center gap-1"
              >
                <div class="absolute -top-7 left-1/2 -translate-x-1/2 hidden group-hover:block bg-popover border text-xs rounded px-1.5 py-0.5 whitespace-nowrap z-10 shadow">
                  {{ fmtWeek(week.week) }}: {{ week.count }}
                </div>
                <div
                  class="w-full rounded-t bg-indigo-500 hover:bg-indigo-400 transition-colors"
                  :style="{ height: `${(week.count / weeklyMax) * (expanded ? 240 : 128)}px`, minHeight: '4px' }"
                />
                <span class="text-[9px] text-muted-foreground rotate-45 origin-left translate-x-1 hidden sm:block">
                  {{ fmtWeek(week.week) }}
                </span>
              </div>
            </div>
          </template>
        </DashboardWidget>

      </div>

      <!-- ── Outcome + Platform + Companies ─────────────────────────────── -->
      <div
        v-if="isVisible('outcome') || isVisible('platform') || isVisible('companies')"
        class="grid grid-cols-1 gap-4"
        :class="{
          'md:grid-cols-3': isVisible('outcome') && isVisible('platform') && isVisible('companies'),
          'md:grid-cols-2': [isVisible('outcome'), isVisible('platform'), isVisible('companies')].filter(Boolean).length === 2,
        }"
      >

        <!-- Outcome Breakdown -->
        <DashboardWidget
          v-if="isVisible('outcome')"
          title="Outcome Breakdown"
          subtitle="Where applications ended up"
          @remove="removeWidget('outcome')"
        >
          <template #default="{ expanded }">
            <div v-if="outcomeSegments.length === 0" class="flex items-center justify-center h-32 text-xs text-muted-foreground">
              No outcome data yet
            </div>
            <div v-else class="flex flex-col items-center gap-4">
              <svg :viewBox="'0 0 128 128'" :class="['−rotate-90', expanded ? 'w-48 h-48' : 'w-32 h-32']" style="transform: rotate(-90deg)">
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
          </template>
        </DashboardWidget>

        <!-- By Platform -->
        <DashboardWidget
          v-if="isVisible('platform')"
          title="By Platform"
          subtitle="Where you found the roles"
          @remove="removeWidget('platform')"
        >
          <template #default>
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
          </template>
        </DashboardWidget>

        <!-- Top Companies -->
        <DashboardWidget
          v-if="isVisible('companies')"
          title="Top Companies"
          subtitle="Most applications sent to"
          @remove="removeWidget('companies')"
        >
          <template #default>
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
          </template>
        </DashboardWidget>

      </div>

      <!-- All widgets hidden -->
      <div
        v-if="!isVisible('stat-cards') && !isVisible('rate-strip') && !isVisible('funnel') && !isVisible('weekly') && !isVisible('outcome') && !isVisible('platform') && !isVisible('companies')"
        class="flex flex-col items-center justify-center h-48 gap-3 text-muted-foreground rounded-xl border border-dashed"
      >
        <LayoutDashboard class="w-8 h-8 opacity-30" />
        <p class="text-sm">All widgets are hidden. Use the <strong>Widgets</strong> button to restore them.</p>
      </div>

    </template>

    <!-- Empty state -->
    <div v-else class="flex flex-col items-center justify-center h-64 gap-3 text-muted-foreground">
      <p class="text-sm">Could not load dashboard data.</p>
    </div>

  </div>
</template>
