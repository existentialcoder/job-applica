from fastapi import HTTPException
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.board import DEFAULT_STAGES, MANDATORY_STAGE_KEYS, MANDATORY_STAGE_LABELS, Board
from ..models.job import Job
from ..schemas.board import BoardBase, BoardCreate, BoardUpdate
from ..schemas.user import UserBase


def _validate_mandatory_stages(stages: list[dict], key_renames: dict[str, str] | None = None) -> None:
    if key_renames and (mandatory_renamed := set(key_renames) & set(MANDATORY_STAGE_KEYS)):
        raise HTTPException(status_code=400, detail=f'Cannot rename mandatory stage(s): {", ".join(mandatory_renamed)}')

    keys_in_order = [s['key'] for s in stages]

    missing = [k for k in MANDATORY_STAGE_KEYS if k not in keys_in_order]
    if missing:
        raise HTTPException(status_code=400, detail=f'Cannot remove mandatory stage(s): {", ".join(missing)}')

    present_mandatory = [k for k in keys_in_order if k in MANDATORY_STAGE_KEYS]
    if present_mandatory != MANDATORY_STAGE_KEYS:
        raise HTTPException(status_code=400, detail='Mandatory stages must stay in their original relative order')

    for s in stages:
        if s['key'] in MANDATORY_STAGE_LABELS and s['label'] != MANDATORY_STAGE_LABELS[s['key']]:
            raise HTTPException(status_code=400, detail=f'Cannot rename mandatory stage "{s["key"]}"')


async def get_boards(db: AsyncSession, user: UserBase) -> list[BoardBase]:
    result = await db.execute(
        select(Board).where(Board.user_id == user.id).order_by(Board.is_default.desc(), Board.created_at)
    )
    boards = [BoardBase.model_validate(b) for b in result.scalars().all()]
    for board in boards:
        job_count_result = await db.execute(select(func.count(Job.id)).where(Job.board_id == board.id))
        board.number_of_jobs = job_count_result.scalar()
    return boards


async def get_board(db: AsyncSession, user: UserBase, board_id: int) -> BoardBase | None:
    result = await db.execute(select(Board).where(Board.user_id == user.id, Board.id == board_id))
    board = result.scalar_one_or_none()
    return BoardBase.model_validate(board) if board else None


async def get_default_board_id(db: AsyncSession, user_id: int) -> int | None:
    result = await db.execute(select(Board.id).where(Board.user_id == user_id, Board.is_default == True))
    row = result.first()
    return row[0] if row else None


async def create_board(db: AsyncSession, user: UserBase, board_in: BoardCreate) -> BoardBase:
    existing_count_result = await db.execute(select(func.count(Board.id)).where(Board.user_id == user.id))
    is_first = existing_count_result.scalar() == 0

    stages = [s.model_dump() for s in board_in.stages] if board_in.stages else DEFAULT_STAGES
    if board_in.stages:
        _validate_mandatory_stages(stages)
    board = Board(
        name=board_in.name,
        color=board_in.color,
        description=board_in.description,
        stages=stages,
        user_id=user.id,
        is_default=is_first,
    )
    db.add(board)
    await db.commit()
    await db.refresh(board)
    return BoardBase.model_validate(board)


async def update_board(db: AsyncSession, user: UserBase, board_id: int, board_in: BoardUpdate) -> BoardBase | None:
    result = await db.execute(select(Board).where(Board.user_id == user.id, Board.id == board_id))
    board = result.scalar_one_or_none()
    if not board:
        return None

    if board_in.name is not None:
        board.name = board_in.name
    if board_in.color is not None:
        board.color = board_in.color
    if board_in.description is not None:
        board.description = board_in.description

    if board_in.stages is not None:
        new_stages = [s.model_dump() for s in board_in.stages]
        _validate_mandatory_stages(new_stages, board_in.key_renames)
        renamed_old_keys: set[str] = set()

        if board_in.key_renames:
            for old_key, new_key in board_in.key_renames.items():
                await db.execute(
                    update(Job).where(Job.board_id == board_id, Job.status == old_key).values(status=new_key)
                )
            renamed_old_keys = set(board_in.key_renames.keys())

        new_keys = {s['key'] for s in new_stages}
        old_keys = {s['key'] for s in (board.stages or [])}
        removed_keys = (old_keys - new_keys) - renamed_old_keys
        if removed_keys and new_stages:
            first_stage = new_stages[0]['key']
            await db.execute(
                update(Job)
                .where(Job.board_id == board_id, Job.status.in_(list(removed_keys)))
                .values(status=first_stage)
            )

        board.stages = new_stages

    await db.commit()
    await db.refresh(board)
    return BoardBase.model_validate(board)


async def set_default_board(db: AsyncSession, user: UserBase, board_id: int) -> BoardBase | None:
    result = await db.execute(select(Board).where(Board.user_id == user.id, Board.id == board_id))
    board = result.scalar_one_or_none()
    if not board:
        return None

    await db.execute(update(Board).where(Board.user_id == user.id, Board.is_default == True).values(is_default=False))
    board.is_default = True
    await db.commit()
    await db.refresh(board)
    return BoardBase.model_validate(board)


async def delete_board(db: AsyncSession, user: UserBase, board_id: int) -> bool:
    result = await db.execute(
        select(Board).where(Board.user_id == user.id, Board.id == board_id, Board.is_default == False)
    )
    board = result.scalar_one_or_none()
    if not board:
        return False

    await db.execute(update(Job).where(Job.board_id == board_id).values(board_id=None))
    await db.delete(board)
    await db.commit()
    return True
