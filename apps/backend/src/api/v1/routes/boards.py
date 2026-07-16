from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from ....schemas.board import BoardBase, BoardCreate, BoardUpdate
from ....schemas.user import UserBase
from ....models.board import Board
from ...deps.auth import get_current_user
from ...deps.db import get_db
from ...deps.plan import plan_gate
from ....services import board as board_service

router = APIRouter(prefix='/boards')


@router.get('', response_model=list[BoardBase])
async def list_boards(user: UserBase = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await board_service.get_boards(db, user)


@router.get('/{board_id}', response_model=BoardBase)
async def get_board(board_id: int, user: UserBase = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    board = await board_service.get_board(db, user, board_id)
    if not board:
        raise HTTPException(status_code=404, detail='Board not found')
    return board


@router.post(
    '',
    response_model=BoardBase,
    status_code=201,
    dependencies=[plan_gate('max_job_boards', lambda uid: select(func.count(Board.id)).where(Board.user_id == uid))],
)
async def create_board(board_in: BoardCreate, user: UserBase = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await board_service.create_board(db, user, board_in)


@router.patch('/{board_id}', response_model=BoardBase)
async def update_board(board_id: int, board_in: BoardUpdate, user: UserBase = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    board = await board_service.update_board(db, user, board_id, board_in)
    if not board:
        raise HTTPException(status_code=404, detail='Board not found')
    return board


@router.post('/{board_id}/set-default', response_model=BoardBase)
async def set_default_board(board_id: int, user: UserBase = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    board = await board_service.set_default_board(db, user, board_id)
    if not board:
        raise HTTPException(status_code=404, detail='Board not found')
    return board


@router.delete('/{board_id}')
async def delete_board(board_id: int, user: UserBase = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    success = await board_service.delete_board(db, user, board_id)
    if not success:
        raise HTTPException(status_code=404, detail='Board not found or cannot delete default board')
    return {'detail': 'Board deleted'}
