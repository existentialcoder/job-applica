import os
import json
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from .api.deps.auth import get_current_user
from .api.v1.routes import jobs, companies, auth, skills, boards, dashboard, connected_accounts, features, ats, users
from .core.config import settings
from .core.exceptions import PlanLimitReached
from .db.base_class import Base
from .db.session import engine
from .models import resume as _resume_model  # ensure table is created
from .models import connected_account as _connected_account_model  # ensure table is created


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(title='JobApplica API', lifespan=lifespan)


@app.exception_handler(PlanLimitReached)
async def plan_limit_handler(_: Request, exc: PlanLimitReached):
    return JSONResponse(
        status_code=402,
        content={
            'code': 'PLAN_LIMIT_REACHED',
            'resource': exc.resource,
            'current': exc.current,
            'limit': exc.limit,
            'plan': exc.plan,
        },
    )


@app.get('/health', tags=['Health'], include_in_schema=False)
def health():
    return {'status': 'ok'}

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    # Chrome IDs: 32 lowercase letters. Firefox IDs: UUIDs with hyphens.
    allow_origin_regex=r'(chrome-extension|moz-extension)://[a-z0-9-]+',
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

api_v1_prefix = '/api/v1'

# Public routes (no auth)
app.include_router(features.router, prefix=api_v1_prefix, tags=['Features'])

enabled_routes = [
    { 'tags': ['Jobs'], 'route': jobs },
    { 'tags': ['Companies'], 'route': companies },
    { 'tags': ['Auth'], 'route': auth },
    { 'tags': ['Skills'], 'route': skills },
    { 'tags': ['Boards'], 'route': boards },
    { 'tags': ['Dashboard'], 'route': dashboard },
    { 'tags': ['Connected Accounts'], 'route': connected_accounts },
    { 'tags': ['ATS'], 'route': ats },
    { 'tags': ['Users'], 'route': users },
]

for enabled_route in enabled_routes:
    base_router_args = {'prefix': api_v1_prefix, 'tags': enabled_route['tags']}
    if 'Auth' in enabled_route['tags']:
        router_args = base_router_args
    else:
        router_args = {**base_router_args, 'dependencies': [Depends(get_current_user)]}
    app.include_router(enabled_route['route'].router, **router_args)


app.include_router(
    ats.quick_router,
    prefix=api_v1_prefix,
    tags=['ATS'],
    dependencies=[Depends(get_current_user)],
)

# Serve uploaded files
_uploads_dir = os.path.join(os.path.dirname(__file__), '..', 'uploads')
os.makedirs(_uploads_dir, exist_ok=True)
app.mount('/uploads', StaticFiles(directory=_uploads_dir), name='uploads')
