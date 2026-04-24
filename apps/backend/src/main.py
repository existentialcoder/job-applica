from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.deps.auth import get_current_user
from .api.v1.routes import jobs, companies, auth, skills
from .core.config import settings
from .db.base_class import Base
from .db.session import engine

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
    { 'tags': ['Skills'], 'route': skills }
]

for enabled_route in enabled_routes:
    base_router_args = {'prefix': api_v1_prefix, 'tags': enabled_route['tags']}
    if 'Auth' in enabled_route['tags']:
        router_args = base_router_args
    else:
        router_args = {**base_router_args, 'dependencies': [Depends(get_current_user)]}
    app.include_router(enabled_route['route'].router, **router_args)
