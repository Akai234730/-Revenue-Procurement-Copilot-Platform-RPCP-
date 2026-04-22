from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings
from app.core.exceptions import app_exception_handler, http_exception_handler, unhandled_exception_handler, AppError
from app.core.logging import configure_logging

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging()
    yield


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    debug=settings.app_debug,
    lifespan=lifespan,
)

app.add_exception_handler(AppError, app_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")
