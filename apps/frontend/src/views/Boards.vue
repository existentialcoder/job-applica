<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter
} from '@/components/ui/dialog';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger
} from '@/components/ui/dropdown-menu';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import type { BoardData } from '@/lib/types';
import { useAppStore } from '@/stores/app';
import { useBoardsStore } from '@/stores/boards';

const router = useRouter();
const appStore = useAppStore();
const boardsStore = useBoardsStore();

const isCreateOpen = ref(false);
const newBoardName = ref('');
const newBoardColor = ref('bg-blue-500');
const newBoardDesc = ref('');
const isSaving = ref(false);

// Edit state
const isEditOpen = ref(false);
const editingBoard = ref<BoardData | null>(null);
const editName = ref('');
const editColor = ref('bg-blue-500');
const editDesc = ref('');

// Delete confirm state
const isDeleteOpen = ref(false);
const deletingBoard = ref<BoardData | null>(null);
const isDeleting = ref(false);

const COLOR_OPTIONS = [
  { value: 'bg-blue-500', label: 'Blue' },
  { value: 'bg-violet-500', label: 'Violet' },
  { value: 'bg-emerald-500', label: 'Emerald' },
  { value: 'bg-amber-500', label: 'Amber' },
  { value: 'bg-rose-500', label: 'Rose' },
  { value: 'bg-slate-500', label: 'Slate' },
  { value: 'bg-orange-500', label: 'Orange' },
  { value: 'bg-cyan-500', label: 'Cyan' }
];

async function createBoard() {
  if (!newBoardName.value.trim()) return;
  isSaving.value = true;
  const ok = await boardsStore.createBoard({
    name: newBoardName.value.trim(),
    color: newBoardColor.value,
    description: newBoardDesc.value.trim() || undefined
  });
  if (ok) {
    isCreateOpen.value = false;
    newBoardName.value = '';
    newBoardDesc.value = '';
    newBoardColor.value = 'bg-blue-500';
  }
  isSaving.value = false;
}

function openBoard(board: BoardData) {
  router.push(`/boards/${board.id}`);
}

function openEdit(board: BoardData, e: Event) {
  e.stopPropagation();
  editingBoard.value = board;
  editName.value = board.name;
  editColor.value = board.color ?? 'bg-blue-500';
  editDesc.value = board.description ?? '';
  isEditOpen.value = true;
}

async function saveEdit() {
  if (!editingBoard.value || !editName.value.trim()) return;
  isSaving.value = true;
  const ok = await boardsStore.updateBoard(editingBoard.value.id, {
    name: editName.value.trim(),
    color: editColor.value,
    description: editDesc.value.trim() || undefined
  });
  if (ok) {
    isEditOpen.value = false;
  }
  isSaving.value = false;
}

async function makeDefault(board: BoardData, e: Event) {
  e.stopPropagation();
  await boardsStore.setDefaultBoard(board.id);
}

function openDelete(board: BoardData, e: Event) {
  e.stopPropagation();
  deletingBoard.value = board;
  isDeleteOpen.value = true;
}

async function confirmDelete() {
  if (!deletingBoard.value) return;
  isDeleting.value = true;
  const ok = await boardsStore.deleteBoard(deletingBoard.value.id);
  if (ok) {
    isDeleteOpen.value = false;
    deletingBoard.value = null;
  }
  isDeleting.value = false;
}

onMounted(async () => {
  appStore.setBreadcrumbs([]);
  await boardsStore.fetch();
});

onUnmounted(() => {
  appStore.setBreadcrumbs([]);
});
</script>

<template>
  <div class="flex flex-col gap-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-semibold">Application Boards</h1>
        <p class="text-sm text-muted-foreground mt-0.5">
          Organise your job search into separate boards
        </p>
      </div>
      <div class="flex items-center gap-2">
        <Button variant="outline" @click="router.push('/boards/all')">
          <Icon name="LayoutGrid" class="w-4 h-4 mr-1" />
          All Applications
        </Button>
        <Button @click="isCreateOpen = true">
          <Icon name="Plus" class="w-4 h-4 mr-1" />
          New Board
        </Button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="boardsStore.loading" class="flex justify-center py-16">
      <Icon name="LoaderCircle" :size="24" default-class="animate-spin text-muted-foreground" />
    </div>

    <!-- Empty state -->
    <div
      v-else-if="boardsStore.boards.length === 0"
      class="flex flex-col items-center justify-center py-20 gap-4 text-center"
    >
      <div class="w-14 h-14 rounded-2xl bg-muted flex items-center justify-center">
        <Icon name="LayoutDashboard" class="w-7 h-7 text-muted-foreground" />
      </div>
      <div>
        <p class="font-medium">No boards yet</p>
        <p class="text-sm text-muted-foreground mt-0.5">
          Create a board to start tracking applications
        </p>
      </div>
    </div>

    <!-- Board grid -->
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      <div
        v-for="board in boardsStore.boards"
        :key="board.id"
        class="group relative flex flex-col rounded-xl border border-border bg-card hover:shadow-md hover:border-primary/30 transition-all cursor-pointer"
        @click="openBoard(board)"
      >
        <div class="p-4 flex flex-col gap-1.5 flex-1">
          <!-- Name row -->
          <div class="flex items-start justify-between gap-2">
            <div class="flex items-center gap-2 min-w-0">
              <span
                :class="[
                  'w-2.5 h-2.5 rounded-full flex-shrink-0 mt-0.5',
                  board.color || 'bg-blue-500'
                ]"
              />
              <h3 class="font-semibold text-base leading-tight truncate">{{ board.name }}</h3>
              <span
                v-if="board.is_default"
                class="text-xs bg-primary/10 text-primary px-1.5 py-0.5 rounded flex-shrink-0"
              >
                Default
              </span>
            </div>

            <!-- Three-dots menu -->
            <DropdownMenu>
              <DropdownMenuTrigger as-child @click.stop>
                <button
                  class="opacity-0 group-hover:opacity-100 transition-opacity p-1 rounded hover:bg-muted text-muted-foreground hover:text-foreground flex-shrink-0"
                >
                  <Icon name="EllipsisVertical" :size="16" />
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" @click.stop>
                <DropdownMenuItem @click.stop="openEdit(board, $event)">
                  <Icon name="Pencil" class="w-4 h-4 mr-2" /> Edit
                </DropdownMenuItem>
                <DropdownMenuItem v-if="!board.is_default" @click.stop="makeDefault(board, $event)">
                  <Icon name="Star" class="w-4 h-4 mr-2" /> Make Default
                </DropdownMenuItem>
                <template v-if="!board.is_default">
                  <DropdownMenuSeparator />
                  <DropdownMenuItem
                    class="text-destructive focus:text-destructive"
                    @click.stop="openDelete(board, $event)"
                  >
                    <Icon name="Trash" class="w-4 h-4 mr-2" /> Delete Board
                  </DropdownMenuItem>
                </template>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>

          <!-- Description -->
          <p v-if="board.description" class="text-sm text-muted-foreground line-clamp-2">
            {{ board.description }}
          </p>
          <p v-else class="text-sm text-muted-foreground/40 italic">No description</p>
        </div>

        <div
          class="px-4 py-2 border-t border-border/50 bg-muted/20 flex items-center justify-between"
        >
          <span class="text-xs text-muted-foreground">{{ board.stages.length }} stages</span>
          <span class="text-xs text-muted-foreground"
            >{{ board.number_of_jobs }} job application{{
              board.number_of_jobs !== 1 ? 's' : ''
            }}</span
          >
          <Icon
            name="ArrowRight"
            class="w-4 h-4 text-muted-foreground group-hover:text-primary transition-colors"
          />
        </div>
      </div>
    </div>

    <!-- Create board dialog -->
    <Dialog v-model:open="isCreateOpen">
      <DialogContent class="max-w-md">
        <DialogHeader>
          <DialogTitle>New Board</DialogTitle>
        </DialogHeader>
        <div class="flex flex-col gap-4 py-2">
          <div class="flex flex-col gap-1.5">
            <Label>Board Name <span class="text-destructive">*</span></Label>
            <Input
              v-model="newBoardName"
              placeholder="e.g. Full-time 2025"
              @keyup.enter="createBoard"
            />
          </div>
          <div class="flex flex-col gap-1.5">
            <Label>Description</Label>
            <Input v-model="newBoardDesc" placeholder="Description" />
          </div>
          <div class="flex flex-col gap-1.5">
            <Label>Color</Label>
            <div class="flex flex-wrap gap-2">
              <button
                v-for="opt in COLOR_OPTIONS"
                :key="opt.value"
                :class="[
                  'w-7 h-7 rounded-full transition-all',
                  opt.value,
                  newBoardColor === opt.value
                    ? 'ring-2 ring-offset-2 ring-primary scale-110'
                    : 'hover:scale-105'
                ]"
                :title="opt.label"
                @click="newBoardColor = opt.value"
              />
            </div>
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" @click="isCreateOpen = false">Cancel</Button>
          <Button @click="createBoard" :disabled="!newBoardName.trim() || isSaving">
            {{ isSaving ? 'Creating...' : 'Create Board' }}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>

    <Dialog v-model:open="isEditOpen">
      <DialogContent class="max-w-md">
        <DialogHeader>
          <DialogTitle>Edit Board</DialogTitle>
        </DialogHeader>
        <div class="flex flex-col gap-4 py-2">
          <div class="flex flex-col gap-1.5">
            <Label>Board Name <span class="text-destructive">*</span></Label>
            <Input v-model="editName" placeholder="e.g. Full-time 2025" @keyup.enter="saveEdit" />
          </div>
          <div class="flex flex-col gap-1.5">
            <Label>Description</Label>
            <Input v-model="editDesc" placeholder="Description" />
          </div>
          <div class="flex flex-col gap-1.5">
            <Label>Color</Label>
            <div class="flex flex-wrap gap-2">
              <button
                v-for="opt in COLOR_OPTIONS"
                :key="opt.value"
                :class="[
                  'w-7 h-7 rounded-full transition-all',
                  opt.value,
                  editColor === opt.value
                    ? 'ring-2 ring-offset-2 ring-primary scale-110'
                    : 'hover:scale-105'
                ]"
                :title="opt.label"
                @click="editColor = opt.value"
              />
            </div>
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" @click="isEditOpen = false">Cancel</Button>
          <Button @click="saveEdit" :disabled="!editName.trim() || isSaving">
            {{ isSaving ? 'Saving...' : 'Save Changes' }}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>

    <!-- Delete confirm dialog -->
    <Dialog v-model:open="isDeleteOpen">
      <DialogContent class="max-w-sm">
        <DialogHeader>
          <DialogTitle>Delete Board</DialogTitle>
        </DialogHeader>
        <div class="py-2">
          <p class="text-sm text-muted-foreground">
            Are you sure you want to delete
            <strong class="text-foreground">{{ deletingBoard?.name }}</strong
            >? All jobs in this board will be permanently deleted. This action cannot be undone.
          </p>
        </div>
        <DialogFooter>
          <Button variant="outline" @click="isDeleteOpen = false" :disabled="isDeleting"
            >Cancel</Button
          >
          <Button variant="destructive" @click="confirmDelete" :disabled="isDeleting">
            {{ isDeleting ? 'Deleting...' : 'Delete Board' }}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  </div>
</template>
