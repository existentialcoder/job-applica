<script setup lang="ts">
import { ref, watch, nextTick } from 'vue';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { COLOR_PALETTE, DEFAULT_BOARD_STAGES, MANDATORY_STAGE_KEYS } from '@/lib/constants';
import type { BoardData, StageData } from '@/lib/types';
import StageBadge from './StageBadge.vue';

const props = defineProps<{
  open: boolean
  board: BoardData
}>();

const emit = defineEmits<{
  (e: 'update:open', val: boolean): void
  (
    e: 'save',
    payload: {
      name: string
      description: string
      color: string
      stages: StageData[]
      key_renames: Record<string, string>
    }
  ): void
}>();

const name = ref('');
const description = ref('');
const color = ref('bg-blue-500');
const stages = ref<StageData[]>([]);
const activeTab = ref<'general' | 'stages'>('general');

function isMandatory(key: string): boolean {
  return MANDATORY_STAGE_KEYS.includes(key);
}

// Inline stage rename state
const editingIndex = ref<number | null>(null);
const editingLabel = ref('');
const keyRenames = ref<Record<string, string>>({});

// Add stage inline
const showAddStage = ref(false);
const newStageName = ref('');
const newStageColor = ref(COLOR_PALETTE[0].value);
const addInputRef = ref<HTMLInputElement | null>(null);

watch(
  () => props.open,
  (open) => {
    if (open) {
      name.value = props.board.name;
      description.value = props.board.description ?? '';
      color.value = props.board.color ?? 'bg-blue-500';
      // Auto-detect key/label mismatches from old bug and queue them as renames
      const renames: Record<string, string> = {};
      const boardStages = props.board.stages.length ? props.board.stages : DEFAULT_BOARD_STAGES;
      stages.value = boardStages.map((s) => {
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
  }
);

function getNextColor(): string {
  const used = stages.value.map((s) => s.color);
  return COLOR_PALETTE.find((c) => !used.includes(c.value))?.value ?? COLOR_PALETTE[0].value;
}

function startEditLabel(i: number) {
  if (isMandatory(stages.value[i].key)) {
    return;
  }
  editingIndex.value = i;
  editingLabel.value = stages.value[i].label;
}

function commitEditLabel() {
  if (editingIndex.value === null) return;
  if (isMandatory(stages.value[editingIndex.value].key)) {
    editingIndex.value = null;
    return;
  }
  const label = editingLabel.value.trim();
  if (label && label !== stages.value[editingIndex.value].label) {
    const oldKey = stages.value[editingIndex.value].key;
    const newKey = label;
    // Track the rename chain: if the old key was itself a rename target, update the chain
    const originalKey =
      Object.keys(keyRenames.value).find((k) => keyRenames.value[k] === oldKey) ?? oldKey;
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
  newStageColor.value = getNextColor();
  await nextTick();
  addInputRef.value?.focus();
}

function cancelAddStage() {
  showAddStage.value = false;
  newStageName.value = '';
}

function submitAddStage() {
  const key = newStageName.value.trim();
  if (!key) return;
  if (stages.value.some((s) => s.key.toLowerCase() === key.toLowerCase())) return;
  stages.value.push({ key, label: key, color: newStageColor.value });
  newStageName.value = '';
  showAddStage.value = false;
}

function removeStage(index: number) {
  if (isMandatory(stages.value[index].key)) return;
  stages.value.splice(index, 1);
}

function moveUp(index: number) {
  if (index === 0) return;
  if (isMandatory(stages.value[index].key)) return;
  const tmp = stages.value[index - 1];
  stages.value[index - 1] = stages.value[index];
  stages.value[index] = tmp;
}

function moveDown(index: number) {
  if (index === stages.value.length - 1) return;
  if (isMandatory(stages.value[index].key)) return;
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
    key_renames: keyRenames.value
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
      <Tabs v-model="activeTab" class="mb-4">
        <TabsList>
          <TabsTrigger value="general">General</TabsTrigger>
          <TabsTrigger value="stages">Stages</TabsTrigger>
        </TabsList>
      </Tabs>

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
              v-for="opt in COLOR_PALETTE"
              :key="opt.value"
              :class="[
                'w-7 h-7 rounded-full transition-all',
                opt.value,
                color === opt.value
                  ? 'ring-2 ring-offset-2 ring-primary scale-110'
                  : 'hover:scale-105'
              ]"
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
            <StageBadge :color="stage.color" class="flex-1">
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
              <!-- Display label (click to edit, unless mandatory) -->
              <span
                v-else
                :class="[
                  'flex-1 text-sm transition-colors',
                  isMandatory(stage.key)
                    ? 'text-muted-foreground'
                    : 'cursor-pointer hover:text-primary'
                ]"
                :title="
                  isMandatory(stage.key) ? 'Standard stage — cannot be renamed' : 'Click to rename'
                "
                @click="startEditLabel(i)"
                >{{ stage.label }}</span
              >

              <Icon
                v-if="isMandatory(stage.key)"
                name="Lock"
                class="w-3 h-3 text-muted-foreground/60 flex-shrink-0"
              />
            </StageBadge>

            <!-- Reorder + remove — hidden entirely for locked stages, not just disabled -->
            <template v-if="!isMandatory(stage.key)">
              <button
                class="p-0.5 text-muted-foreground hover:text-foreground disabled:opacity-30"
                :disabled="i === 0"
                @click="moveUp(i)"
              >
                <Icon name="ChevronUp" :size="14" :stroke-width="2.5" />
              </button>
              <button
                class="p-0.5 text-muted-foreground hover:text-foreground disabled:opacity-30"
                :disabled="i === stages.length - 1"
                @click="moveDown(i)"
              >
                <Icon name="ChevronDown" :size="14" :stroke-width="2.5" />
              </button>

              <button
                class="p-0.5 text-muted-foreground hover:text-destructive disabled:opacity-30 transition-colors"
                :disabled="stages.length <= 1"
                @click="removeStage(i)"
                title="Remove stage"
              >
                <Icon name="X" :size="14" :stroke-width="2" />
              </button>
            </template>
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
            <Icon name="Plus" :size="16" :stroke-width="2" />
            Add a stage
          </button>
        </div>
        <div v-else class="flex flex-col gap-2 p-3 rounded-md border border-border bg-muted/20">
          <div class="flex flex-wrap gap-1.5">
            <button
              v-for="c in COLOR_PALETTE"
              :key="c.value"
              type="button"
              :class="[
                'w-5 h-5 rounded-full flex-shrink-0 transition-all',
                c.value,
                newStageColor === c.value
                  ? 'ring-2 ring-offset-2 ring-primary scale-110'
                  : 'hover:scale-105'
              ]"
              :title="c.label"
              @click="newStageColor = c.value"
            />
          </div>
          <input
            ref="addInputRef"
            v-model="newStageName"
            class="w-full rounded border border-input bg-background px-2 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-ring"
            placeholder="Stage name..."
            @keyup.enter="submitAddStage"
            @keyup.escape="cancelAddStage"
          />
          <div class="flex gap-1.5">
            <button
              class="flex-1 text-xs py-1.5 rounded bg-primary text-primary-foreground font-medium disabled:opacity-50"
              :disabled="!newStageName.trim()"
              @click="submitAddStage"
            >
              Add
            </button>
            <button
              class="flex-1 text-xs py-1.5 rounded border border-border text-muted-foreground hover:text-foreground"
              @click="cancelAddStage"
            >
              Cancel
            </button>
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
