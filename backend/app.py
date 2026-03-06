from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from sqlalchemy import engine
from backend.Middleware.limmiter import rate_limit_middleware
from starlette.middleware.base import BaseHTTPMiddleware

from backend.Model.model import Base
from backend.Router import user,auth


app = FastAPI()
@asynccontextmanager
async def lifespan(app: FastAPI):
    # This triggers table creation on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app.add_middleware(BaseHTTPMiddleware,dispatch = rate_limit_middleware)


app.include_router(user.router)
app.include_router(auth.router)

@app.get("/")
def root():
    return {"Welcome to Resume Analyzer"}


