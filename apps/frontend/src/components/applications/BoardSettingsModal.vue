<script setup lang="ts">
import { ref, watch, nextTick } from 'vue';
import type { BoardData, StageData } from '@/lib/types';
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

const props = defineProps<{
  open: boolean
  board: BoardData
}>();

const emit = defineEmits<{
  (e: 'update:open', val: boolean): void
  (e: 'save', payload: { name: string; description: string; color: string; stages: StageData[]; key_renames: Record<string, string> }): void
}>();

const STAGE_COLORS = [
  'bg-slate-500', 'bg-blue-500', 'bg-violet-500', 'bg-emerald-500',
  'bg-amber-500', 'bg-rose-500', 'bg-orange-500', 'bg-cyan-500',
  'bg-pink-500', 'bg-teal-500', 'bg-indigo-500', 'bg-zinc-400',
];

const COLOR_OPTIONS = [
  { value: 'bg-blue-500', label: 'Blue' },
  { value: 'bg-violet-500', label: 'Violet' },
  { value: 'bg-emerald-500', label: 'Emerald' },
  { value: 'bg-amber-500', label: 'Amber' },
  { value: 'bg-rose-500', label: 'Rose' },
  { value: 'bg-slate-500', label: 'Slate' },
  { value: 'bg-orange-500', label: 'Orange' },
  { value: 'bg-cyan-500', label: 'Cyan' },
];

const name = ref('');
const description = ref('');
const color = ref('bg-blue-500');
const stages = ref<StageData[]>([]);
const isSaving = ref(false);
const activeTab = ref<'general' | 'stages'>('general');

// Inline stage rename state
const editingIndex = ref<number | null>(null);
const editingLabel = ref('');
const keyRenames = ref<Record<string, string>>({});

// Add stage inline
const showAddStage = ref(false);
const newStageName = ref('');
const addInputRef = ref<HTMLInputElement | null>(null);

watch(() => props.open, (open) => {
  if (open) {
    name.value = props.board.name;
    description.value = props.board.description ?? '';
    color.value = props.board.color ?? 'bg-blue-500';
    // Auto-detect key/label mismatches from old bug and queue them as renames
    const renames: Record<string, string> = {};
    stages.value = props.board.stages.map(s => {
      if (s.key !== s.label) {
        renames[s.key] = s.label;
        return { ...s, key: s.label };
      }
      return { ...s };
    });
    keyRenames.value = renames;
    editingIndex.value = null;
    showAddStage.value = false;
    newStageName.value = '';
    activeTab.value = 'general';
  }
});

function getNextColor(): string {
  const used = stages.value.map(s => s.color);
  return STAGE_COLORS.find(c => !used.includes(c)) ?? STAGE_COLORS[0];
}

function startEditLabel(i: number) {
  editingIndex.value = i;
  editingLabel.value = stages.value[i].label;
}

function commitEditLabel() {
  if (editingIndex.value === null) return;
  const label = editingLabel.value.trim();
  if (label && label !== stages.value[editingIndex.value].label) {
    const oldKey = stages.value[editingIndex.value].key;
    const newKey = label;
    // Track the rename chain: if the old key was itself a rename target, update the chain
    const originalKey = Object.keys(keyRenames.value).find(k => keyRenames.value[k] === oldKey) ?? oldKey;
    if (originalKey !== newKey) {
      keyRenames.value = { ...keyRenames.value, [originalKey]: newKey };
    }
    stages.value[editingIndex.value] = { ...stages.value[editingIndex.value], key: newKey, label };
  }
  editingIndex.value = null;
}

function cancelEditLabel() {
  editingIndex.value = null;
}

async function openAddStage() {
  showAddStage.value = true;
  await nextTick();
  addInputRef.value?.focus();
}

function submitAddStage() {
  const key = newStageName.value.trim();
  if (!key) return;
  if (stages.value.some(s => s.key.toLowerCase() === key.toLowerCase())) return;
  stages.value.push({ key, label: key, color: getNextColor() });
  newStageName.value = '';
  showAddStage.value = false;
}

function removeStage(index: number) {
  stages.value.splice(index, 1);
}

function moveUp(index: number) {
  if (index === 0) return;
  const tmp = stages.value[index - 1];
  stages.value[index - 1] = stages.value[index];
  stages.value[index] = tmp;
}

function moveDown(index: number) {
  if (index === stages.value.length - 1) return;
  const tmp = stages.value[index + 1];
  stages.value[index + 1] = stages.value[index];
  stages.value[index] = tmp;
}

function handleSave() {
  if (!name.value.trim() || stages.value.length === 0) return;
  emit('save', {
    name: name.value.trim(),
    description: description.value.trim(),
    color: color.value,
    stages: stages.value,
    key_renames: keyRenames.value,
  });
}
</script>

<template>
  <Dialog :open="open" @update:open="$emit('update:open', $event)">
    <DialogContent class="max-w-lg max-h-[90vh] overflow-y-auto">
      <DialogHeader>
        <DialogTitle>Board Settings</DialogTitle>
      </DialogHeader>

      <!-- Tabs -->
      <div class="flex border-b border-border mb-4">
        <button
          :class="['px-4 py-2 text-sm font-medium border-b-2 transition-colors', activeTab === 'general' ? 'border-primary text-primary' : 'border-transparent text-muted-foreground hover:text-foreground']"
          @click="activeTab = 'general'"
        >General</button>
        <button
          :class="['px-4 py-2 text-sm font-medium border-b-2 transition-colors', activeTab === 'stages' ? 'border-primary text-primary' : 'border-transparent text-muted-foreground hover:text-foreground']"
          @click="activeTab = 'stages'"
        >Stages</button>
      </div>

      <!-- General tab -->
      <div v-if="activeTab === 'general'" class="flex flex-col gap-4">
        <div class="flex flex-col gap-1.5">
          <Label>Board Name <span class="text-destructive">*</span></Label>
          <Input v-model="name" placeholder="e.g. Full-time 2025" />
        </div>
        <div class="flex flex-col gap-1.5">
          <Label>Description</Label>
          <Input v-model="description" placeholder="Description" />
        </div>
        <div class="flex flex-col gap-1.5">
          <Label>Board Color</Label>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="opt in COLOR_OPTIONS"
              :key="opt.value"
              :class="['w-7 h-7 rounded-full transition-all', opt.value, color === opt.value ? 'ring-2 ring-offset-2 ring-primary scale-110' : 'hover:scale-105']"
              :title="opt.label"
              @click="color = opt.value"
            />
          </div>
        </div>
      </div>

      <!-- Stages tab -->
      <div v-else-if="activeTab === 'stages'" class="flex flex-col gap-3">
        <p class="text-xs text-muted-foreground">
          Click a stage name to rename it. Jobs removed from a stage move to the first stage.
        </p>

        <!-- Stage list -->
        <div class="flex flex-col gap-1.5">
          <div
            v-for="(stage, i) in stages"
            :key="stage.key"
            class="flex items-center gap-2 px-2 py-1.5 rounded-md border border-border bg-muted/30 group/stage"
          >
            <div :class="['w-3 h-3 rounded-full flex-shrink-0', stage.color]" />

            <!-- Inline edit input -->
            <input
              v-if="editingIndex === i"
              v-model="editingLabel"
              class="flex-1 text-sm bg-transparent border-b border-primary outline-none px-0.5 min-w-0"
              @keyup.enter="commitEditLabel"
              @keyup.escape="cancelEditLabel"
              @blur="commitEditLabel"
              autofocus
            />
            <!-- Display label (click to edit) -->
            <span
              v-else
              class="flex-1 text-sm cursor-pointer hover:text-primary transition-colors"
              title="Click to rename"
              @click="startEditLabel(i)"
            >{{ stage.label }}</span>

            <span v-if="i === 0" class="text-xs text-muted-foreground/60 italic flex-shrink-0">first</span>

            <!-- Reorder -->
            <button
              class="p-0.5 text-muted-foreground hover:text-foreground disabled:opacity-30"
              :disabled="i === 0"
              @click="moveUp(i)"
            >
              <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M5 15l7-7 7 7" />
              </svg>
            </button>
            <button
              class="p-0.5 text-muted-foreground hover:text-foreground disabled:opacity-30"
              :disabled="i === stages.length - 1"
              @click="moveDown(i)"
            >
              <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            <!-- Remove -->
            <button
              class="p-0.5 text-muted-foreground hover:text-destructive disabled:opacity-30 transition-colors"
              :disabled="stages.length <= 1"
              @click="removeStage(i)"
              title="Remove stage"
            >
              <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <p v-if="stages.length === 0" class="text-sm text-muted-foreground text-center py-3">
            No stages yet. Add one below.
          </p>
        </div>

        <!-- Add stage (Trello-style inline) -->
        <div v-if="!showAddStage">
          <button
            class="w-full flex items-center gap-2 px-3 py-2 rounded-md border-2 border-dashed border-muted-foreground/20 text-sm text-muted-foreground hover:border-primary/40 hover:text-primary transition-colors"
            @click="openAddStage"
          >
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4" />
            </svg>
            Add a stage
          </button>
        </div>
        <div v-else class="flex flex-col gap-2 p-3 rounded-md border border-border bg-muted/20">
          <div class="flex items-center gap-2">
            <div :class="['w-3 h-3 rounded-full flex-shrink-0', getNextColor()]" />
            <span class="text-xs text-muted-foreground">Color auto-assigned</span>
          </div>
          <input
            ref="addInputRef"
            v-model="newStageName"
            class="w-full rounded border border-input bg-background px-2 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-ring"
            placeholder="Stage name..."
            @keyup.enter="submitAddStage"
            @keyup.escape="showAddStage = false; newStageName = ''"
          />
          <div class="flex gap-1.5">
            <button
              class="flex-1 text-xs py-1.5 rounded bg-primary text-primary-foreground font-medium disabled:opacity-50"
              :disabled="!newStageName.trim()"
              @click="submitAddStage"
            >Add</button>
            <button
              class="flex-1 text-xs py-1.5 rounded border border-border text-muted-foreground hover:text-foreground"
              @click="showAddStage = false; newStageName = ''"
            >Cancel</button>
          </div>
        </div>
      </div>

      <DialogFooter>
        <Button variant="outline" @click="$emit('update:open', false)">Cancel</Button>
        <Button @click="handleSave" :disabled="!name.trim() || stages.length === 0">
          Save Changes
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
