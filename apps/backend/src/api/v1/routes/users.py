from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ....schemas import user as schemas
from ...deps.db import get_db
from ....services import user as user_service

# router = APIRouter(prefix='/users')

# @router.post('/signup', description='Create new user', description='User signup API')
# async def signup_user(user_data: schemas.UserSignup, db: Session = Depends(get_db)):
#     await user_service.create_user(user_data, db)
