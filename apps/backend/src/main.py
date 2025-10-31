from fastapi import FastAPI
from .api.v1.routes import jobs
from .models import company, job, skill, user
from .db.base_class import Base
from .db.session import engine

# Ensure tables are created
Base.metadata.create_all(bind=engine)

app = FastAPI(title='JobApplica API')

api_v1_prefix = '/api/v1'

app.include_router(jobs.router, prefix=api_v1_prefix, tags=['Jobs'])
# app.include_router(users.router, prefix=api_v1_prefix, tags=['Users'])
# app.include_router(plugins.router, prefix=api_v1_prefix, tags=['Plugins'])
# app.include_router(auth.router, prefix=api_v1_prefix, tags=['Auth'])
# app.include_router(health.router, prefix=api_v1_prefix, tags=['Health'])
