from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ....schemas import user as schemas
from ...deps.db import get_db
from ....services import user_service

router = APIRouter(prefix='/users')

@router.post('/', description='Create new user')


