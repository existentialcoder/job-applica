import asyncio
import os
from contextlib import asynccontextmanager
from enum import Enum

from fastapi import APIRouter, Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from .api.deps.auth import get_current_user
from .api.v1.routes import (
    ats,
    auth,
    boards,
    companies,
    connected_accounts,
    dashboard,
    features,
    geo,
    jobs,
    locations,
    skills,
    users,
)
from .core.config import settings
from .core.constants import Constants
from .core.exceptions import PlanLimitReached
from .core.logger import configure_logging
from .db.base_class import Base
from .db.session import engine
from .jobs import extract_resume as extract_resume_job
from .services.redaction import RedactionLeak

configure_logging(settings.LOG_LEVEL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # Held on app.state so the task isn't garbage-collected mid-run.
    app.state.resume_interrupted = asyncio.create_task(extract_resume_job.resume_interrupted())
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


@app.exception_handler(RedactionLeak)
async def redaction_leak_handler(_: Request, __: RedactionLeak):
    return JSONResponse(status_code=422, content={'code': 'CV_UNREADABLE'})


@app.get('/health', tags=['Health'], include_in_schema=False)
def health():
    return {'status': 'ok', 'commit': settings.GIT_SHA}


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_origin_regex=r'(chrome-extension|moz-extension)://[a-z0-9-]+',
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

PUBLIC_ROUTERS: list[tuple[APIRouter, list[str | Enum]]] = [
    (features.router, ['Features']),
    (auth.router, ['Auth']),
    (users.public_router, ['Users']),
]

PROTECTED_ROUTERS: list[tuple[APIRouter, list[str | Enum]]] = [
    (jobs.router, ['Jobs']),
    (companies.router, ['Companies']),
    (locations.router, ['Locations']),
    (skills.router, ['Skills']),
    (boards.router, ['Boards']),
    (dashboard.router, ['Dashboard']),
    (connected_accounts.router, ['Connected Accounts']),
    (ats.router, ['ATS']),
    (ats.quick_router, ['ATS']),
    (users.router, ['Users']),
    (geo.router, ['Geo']),
]

for public_router, tags in PUBLIC_ROUTERS:
    app.include_router(public_router, prefix=Constants.API_V1_PREFIX, tags=tags)

for protected_router, tags in PROTECTED_ROUTERS:
    app.include_router(
        protected_router,
        prefix=Constants.API_V1_PREFIX,
        tags=tags,
        dependencies=[Depends(get_current_user)],
    )

if settings.APP_ENV == 'local':
    _uploads_dir = os.path.join(os.path.dirname(__file__), '..', 'uploads')
    os.makedirs(_uploads_dir, exist_ok=True)
    app.mount('/uploads', StaticFiles(directory=_uploads_dir), name='uploads')

_email_assets_dir = os.path.join(os.path.dirname(__file__), 'templates', 'email', 'assets')
app.mount('/email-assets', StaticFiles(directory=_email_assets_dir), name='email-assets')
