from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings

from app.api.v1.accounts import router as accounts_router
from app.api.v1.snapshots import router as snapshots_router
from app.api.v1.net_worth import router as net_worth_router


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Personal Net Worth Automation API. "
        "Tracks financial accounts, monthly snapshots "
        "and net worth."
    ),
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    accounts_router,
    prefix=settings.api_prefix,
)

app.include_router(
    snapshots_router,
    prefix=settings.api_prefix,
)

app.include_router(
    net_worth_router,
    prefix=settings.api_prefix,
)


@app.get(
    "/",
    tags=["System"],
)
async def root():

    return {
        "application": settings.app_name,
        "version": settings.app_version,
        "status": "running",
    }


@app.get(
    "/health",
    tags=["System"],
)
async def health():

    return {
        "status": "healthy",
    }