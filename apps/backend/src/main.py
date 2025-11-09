from fastapi import FastAPI
from .api.v1.routes import jobs, companies
from .models import company, job, skill, user
from .db.base_class import Base
from .db.session import engine

# Ensure tables are created
Base.metadata.create_all(bind=engine)

app = FastAPI(title='JobApplica API')

api_v1_prefix = '/api/v1'

enabled_routes = [
    { 'tags': ['Jobs'], 'route': jobs },
    { 'tags': ['Companies'], 'route': companies },
    # { 'tags': ['Skills'], 'route': skills }
]

for enabled_route in enabled_routes:
    app.include_router(enabled_route['route'].router, prefix=api_v1_prefix, tags=enabled_route['tags'])
