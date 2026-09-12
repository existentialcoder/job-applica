import { DEFAULT_BOARD_STAGES, MANDATORY_STAGE_KEYS } from './constants';
import type { BoardData, StageData } from './types';

export function findStage(
  boards: BoardData[],
  boardId: number | undefined,
  label: string | null | undefined
): StageData | undefined {
  if (!label) {
    return undefined;
  }
  const board = boards.find((b) => b.id === boardId);
  const stages = board?.stages.length ? board.stages : DEFAULT_BOARD_STAGES;
  return stages.find((s) => s.label === label);
}

// Mandatory stages never persist a color server-side — it's resolved from the
// frontend default list here. Only custom (non-mandatory) stages keep a stored color.
export function resolveStageColor(stage: { key: string; color?: string | null }): string {
  if (MANDATORY_STAGE_KEYS.includes(stage.key)) {
    return DEFAULT_BOARD_STAGES.find((s) => s.key === stage.key)?.color ?? '';
  }
  return stage.color ?? '';
}

export function normalizeStages(stages: StageData[]): StageData[] {
  return stages.map((s) => ({ ...s, color: resolveStageColor(s) }));
}

export function normalizeBoard(board: BoardData): BoardData {
  return { ...board, stages: normalizeStages(board.stages) };
}

export function normalizeBoards(boards: BoardData[]): BoardData[] {
  return boards.map(normalizeBoard);
}
