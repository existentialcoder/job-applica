import os
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from .api.deps.auth import get_current_user
from .api.v1.routes import jobs, companies, auth, skills, boards, dashboard, connected_accounts, features, ats, users
from .core.config import settings
from .core.constants import Constants
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
    allow_origin_regex=r'(chrome-extension|moz-extension)://[a-z0-9-]+',
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

PUBLIC_ROUTERS = [
    (features.router, ['Features']),
    (auth.router, ['Auth']),
    (users.public_router, ['Users']),
]

PROTECTED_ROUTERS = [
    (jobs.router, ['Jobs']),
    (companies.router, ['Companies']),
    (skills.router, ['Skills']),
    (boards.router, ['Boards']),
    (dashboard.router, ['Dashboard']),
    (connected_accounts.router, ['Connected Accounts']),
    (ats.router, ['ATS']),
    (ats.quick_router, ['ATS']),
    (users.router, ['Users']),
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

# Serve uploaded files
_uploads_dir = os.path.join(os.path.dirname(__file__), '..', 'uploads')
os.makedirs(_uploads_dir, exist_ok=True)
app.mount('/uploads', StaticFiles(directory=_uploads_dir), name='uploads')
