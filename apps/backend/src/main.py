import os
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .api.deps.auth import get_current_user
from .api.v1.routes import jobs, companies, auth, skills, boards, dashboard
from .core.config import settings
from .db.base_class import Base
from .db.session import engine
from .models import resume as _resume_model  # ensure table is created

# Ensure tables are created
Base.metadata.create_all(bind=engine)

app = FastAPI(title='JobApplica API')

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    # Covers any Chrome/Firefox extension origin (chrome-extension://<id>, moz-extension://<id>)
    allow_origin_regex=r'(chrome-extension|moz-extension)://[a-z0-9]+',
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

api_v1_prefix = '/api/v1'

enabled_routes = [
    { 'tags': ['Jobs'], 'route': jobs },
    { 'tags': ['Companies'], 'route': companies },
    { 'tags': ['Auth'], 'route': auth },
    { 'tags': ['Skills'], 'route': skills },
    { 'tags': ['Boards'], 'route': boards },
    { 'tags': ['Dashboard'], 'route': dashboard },
]

for enabled_route in enabled_routes:
    base_router_args = {'prefix': api_v1_prefix, 'tags': enabled_route['tags']}
    if 'Auth' in enabled_route['tags']:
        router_args = base_router_args
    else:
        router_args = {**base_router_args, 'dependencies': [Depends(get_current_user)]}
    app.include_router(enabled_route['route'].router, **router_args)

# Serve uploaded files
_uploads_dir = os.path.join(os.path.dirname(__file__), '..', 'uploads')
os.makedirs(_uploads_dir, exist_ok=True)
app.mount('/uploads', StaticFiles(directory=_uploads_dir), name='uploads')
