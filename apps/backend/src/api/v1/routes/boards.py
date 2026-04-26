from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ....schemas.board import BoardBase, BoardCreate, BoardUpdate
from ....schemas.user import UserBase
from ...deps.auth import get_current_user
from ...deps.db import get_db
from ....services import board as board_service

router = APIRouter(prefix='/boards')


@router.get('', response_model=list[BoardBase])
def list_boards(user: UserBase = Depends(get_current_user), db: Session = Depends(get_db)):
    return board_service.get_boards(db, user)


@router.get('/{board_id}', response_model=BoardBase)
def get_board(board_id: int, user: UserBase = Depends(get_current_user), db: Session = Depends(get_db)):
    board = board_service.get_board(db, user, board_id)
    if not board:
        raise HTTPException(status_code=404, detail='Board not found')
    return board


@router.post('', response_model=BoardBase, status_code=201)
def create_board(board_in: BoardCreate, user: UserBase = Depends(get_current_user), db: Session = Depends(get_db)):
    return board_service.create_board(db, user, board_in)


@router.patch('/{board_id}', response_model=BoardBase)
def update_board(board_id: int, board_in: BoardUpdate, user: UserBase = Depends(get_current_user), db: Session = Depends(get_db)):
    board = board_service.update_board(db, user, board_id, board_in)
    if not board:
        raise HTTPException(status_code=404, detail='Board not found')
    return board


@router.post('/{board_id}/set-default', response_model=BoardBase)
def set_default_board(board_id: int, user: UserBase = Depends(get_current_user), db: Session = Depends(get_db)):
    board = board_service.set_default_board(db, user, board_id)
    if not board:
        raise HTTPException(status_code=404, detail='Board not found')
    return board


@router.delete('/{board_id}')
def delete_board(board_id: int, user: UserBase = Depends(get_current_user), db: Session = Depends(get_db)):
    success = board_service.delete_board(db, user, board_id)
    if not success:
        raise HTTPException(status_code=404, detail='Board not found or cannot delete default board')
    return {'detail': 'Board deleted'}
