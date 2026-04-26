from sqlalchemy.orm import Session

from ..models.board import Board, DEFAULT_STAGES
from ..schemas.board import BoardBase, BoardCreate, BoardUpdate
from ..schemas.user import UserBase


def get_boards(db: Session, user: UserBase) -> list[BoardBase]:
    boards = (
        db.query(Board)
        .filter(Board.user_id == user.id)
        .order_by(Board.is_default.desc(), Board.created_at)
        .all()
    )
    return [BoardBase.model_validate(b) for b in boards]


def get_board(db: Session, user: UserBase, board_id: int) -> BoardBase | None:
    board = db.query(Board).filter(Board.user_id == user.id, Board.id == board_id).first()
    return BoardBase.model_validate(board) if board else None


def get_default_board_id(db: Session, user_id: int) -> int | None:
    board = db.query(Board.id).filter(Board.user_id == user_id, Board.is_default == True).first()
    return board[0] if board else None


def create_board(db: Session, user: UserBase, board_in: BoardCreate) -> BoardBase:
    stages = [s.model_dump() for s in board_in.stages] if board_in.stages else DEFAULT_STAGES
    board = Board(
        name=board_in.name,
        color=board_in.color,
        description=board_in.description,
        stages=stages,
        user_id=user.id,
        is_default=False,
    )
    db.add(board)
    db.commit()
    db.refresh(board)
    return BoardBase.model_validate(board)


def update_board(db: Session, user: UserBase, board_id: int, board_in: BoardUpdate) -> BoardBase | None:
    from ..models.job import Job

    board = db.query(Board).filter(Board.user_id == user.id, Board.id == board_id).first()
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
        # Migrate jobs for renamed keys (old_key → new_key)
        renamed_old_keys: set[str] = set()
        if board_in.key_renames:
            for old_key, new_key in board_in.key_renames.items():
                db.query(Job).filter(
                    Job.board_id == board_id,
                    Job.status == old_key,
                ).update({'status': new_key}, synchronize_session=False)
            renamed_old_keys = set(board_in.key_renames.keys())
        # Move jobs from completely removed stages to the first remaining stage
        new_keys = {s['key'] for s in new_stages}
        old_keys = {s['key'] for s in (board.stages or [])}
        removed_keys = (old_keys - new_keys) - renamed_old_keys
        if removed_keys and new_stages:
            first_stage = new_stages[0]['key']
            db.query(Job).filter(
                Job.board_id == board_id,
                Job.status.in_(list(removed_keys)),
            ).update({'status': first_stage}, synchronize_session=False)
        board.stages = new_stages
    db.commit()
    db.refresh(board)
    return BoardBase.model_validate(board)


def set_default_board(db: Session, user: UserBase, board_id: int) -> BoardBase | None:
    board = db.query(Board).filter(Board.user_id == user.id, Board.id == board_id).first()
    if not board:
        return None
    # Unset any existing default
    db.query(Board).filter(Board.user_id == user.id, Board.is_default == True).update(
        {'is_default': False}, synchronize_session=False
    )
    board.is_default = True
    db.commit()
    db.refresh(board)
    return BoardBase.model_validate(board)


def delete_board(db: Session, user: UserBase, board_id: int) -> bool:
    board = db.query(Board).filter(
        Board.user_id == user.id,
        Board.id == board_id,
        Board.is_default == False,
    ).first()
    if not board:
        return False
    db.delete(board)
    db.commit()
    return True
