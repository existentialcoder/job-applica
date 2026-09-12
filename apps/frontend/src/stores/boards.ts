import { defineStore } from 'pinia';
import { ref } from 'vue';
import dataservice from '@/lib/dataservice';
import { toast } from '@/lib/toast';
import type { BoardData } from '@/lib/types';

export const useBoardsStore = defineStore('boards', () => {
  const boards = ref<BoardData[]>([]);
  const loaded = ref(false);
  const loading = ref(false);
  let inFlight: Promise<void> | null = null;

  async function fetch(force = false) {
    if (loaded.value && !force) {
      return;
    }
    if (inFlight) {
      return inFlight;
    }
    loading.value = true;
    inFlight = (async () => {
      try {
        const result = await dataservice.getBoards();
        boards.value = Array.isArray(result) ? result : [];
        loaded.value = true;
      } finally {
        loading.value = false;
        inFlight = null;
      }
    })();
    return inFlight;
  }

  async function refresh() {
    return fetch(true);
  }

  async function createBoard(payload: {
    name: string;
    color?: string;
    description?: string;
    stages?: { key: string; label: string; color: string }[];
  }): Promise<boolean> {
    const board = await dataservice.createBoard(payload);
    if (!board) {
      toast.error('Failed to create board');
      return false;
    }
    boards.value.push(board);
    toast.success('Board created');
    return true;
  }

  async function updateBoard(
    boardId: number,
    payload: {
      name?: string;
      stages?: { key: string; label: string; color: string }[];
      key_renames?: Record<string, string>;
      color?: string;
      description?: string;
    },
    opts: { silent?: boolean } = {}
  ): Promise<BoardData | undefined> {
    const updated = await dataservice.updateBoard(boardId, payload);
    if (!updated) {
      if (!opts.silent) toast.error('Failed to update board');
      return;
    }
    const idx = boards.value.findIndex((b) => b.id === updated.id);
    if (idx !== -1) {
      boards.value[idx] = updated;
    }
    if (!opts.silent) toast.success('Board updated');
    return updated;
  }

  async function setDefaultBoard(boardId: number): Promise<boolean> {
    const updated = await dataservice.setDefaultBoard(boardId);
    if (!updated) {
      toast.error('Failed to set default board');
      return false;
    }
    boards.value = boards.value.map((b) => ({ ...b, is_default: b.id === boardId }));
    toast.success(`"${updated.name}" set as default`);
    return true;
  }

  async function deleteBoard(boardId: number): Promise<boolean> {
    const board = boards.value.find((b) => b.id === boardId);
    const ok = await dataservice.deleteBoard(boardId);
    if (!ok) {
      toast.error('Failed to delete board');
      return false;
    }
    boards.value = boards.value.filter((b) => b.id !== boardId);
    toast.success(`"${board?.name ?? 'Board'}" deleted`);
    return true;
  }

  return {
    boards,
    loaded,
    loading,
    fetch,
    refresh,
    createBoard,
    updateBoard,
    setDefaultBoard,
    deleteBoard
  };
});
