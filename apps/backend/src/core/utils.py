from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from .config import settings

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

def create_token(data: dict, expiry: int, expiry_type: str, secret: str, algorithm: str):
    to_encode = data.copy()
    expiry_args = {}
    if expiry_type == 'minutes':
        expiry_args['minutes'] = expiry
    elif expiry_type == 'days':
        expiry_args['days'] = expiry

    expire = datetime.utcnow() + timedelta(**expiry_args)
    to_encode.update({'exp': expire})
    return jwt.encode(to_encode, secret, algorithm=algorithm)
