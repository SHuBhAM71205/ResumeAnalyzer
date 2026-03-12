from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from backend.Core.db import engine
from backend.Middleware.jwt_auth import jwt_auth_middleware
from backend.Middleware.limmiter import global_rate_limit_middleware
from starlette.middleware.base import BaseHTTPMiddleware

from backend.Model.model import Base
from backend.Router import user,auth,resume

#cors

from fastapi.middleware.cors import CORSMiddleware
from backend.Core.config import settings

origin = [
    settings.REACT_APP_FRONTEND_URL
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This triggers table creation on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origin,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(BaseHTTPMiddleware,dispatch = global_rate_limit_middleware)
app.add_middleware(BaseHTTPMiddleware,dispatch = jwt_auth_middleware)


app.include_router(user.router)
app.include_router(auth.router)
app.include_router(resume.router)

@app.get("/")
def root():
    return {"message": "Welcome to Resume Analyzer"}


