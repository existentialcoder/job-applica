from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func

from ..models.board import Board, DEFAULT_STAGES
from ..models.job import Job
from ..schemas.board import BoardBase, BoardCreate, BoardUpdate
from ..schemas.user import UserBase
from ..services import plan as plan_service


async def get_boards(db: AsyncSession, user: UserBase) -> list[BoardBase]:
    result = await db.execute(
        select(Board).where(Board.user_id == user.id).order_by(Board.is_default.desc(), Board.created_at)
    )
    return [BoardBase.model_validate(b) for b in result.scalars().all()]


async def get_board(db: AsyncSession, user: UserBase, board_id: int) -> BoardBase | None:
    result = await db.execute(select(Board).where(Board.user_id == user.id, Board.id == board_id))
    board = result.scalar_one_or_none()
    return BoardBase.model_validate(board) if board else None


async def get_default_board_id(db: AsyncSession, user_id: int) -> int | None:
    result = await db.execute(select(Board.id).where(Board.user_id == user_id, Board.is_default == True))
    row = result.first()
    return row[0] if row else None


async def create_board(db: AsyncSession, user: UserBase, board_in: BoardCreate) -> tuple[BoardBase, dict | None]:
    warning = await plan_service.check_plan_limit(
        db, user.id, user.plan, 'max_job_boards',
        select(func.count(Board.id)).where(Board.user_id == user.id),
    )

    existing_count_result = await db.execute(
        select(func.count(Board.id)).where(Board.user_id == user.id)
    )
    is_first = existing_count_result.scalar() == 0

    stages = [s.model_dump() for s in board_in.stages] if board_in.stages else DEFAULT_STAGES
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
    return BoardBase.model_validate(board), warning


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
                update(Job).where(Job.board_id == board_id, Job.status.in_(list(removed_keys))).values(status=first_stage)
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

    await db.execute(
        update(Board).where(Board.user_id == user.id, Board.is_default == True).values(is_default=False)
    )
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
