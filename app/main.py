from fastapi import FastAPI
from contextlib import asynccontextmanager
from .routes.health import router as health_router
from .routes.clientes import router as clientes_router
from .routes.webhook import router as webhook_router
from .infra.db import init

@asynccontextmanager
async def lifespan(app: FastAPI):
    init()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(health_router, prefix="/health", tags=["health"])
app.include_router(clientes_router, prefix="/clientes", tags=["clientes"])
app.include_router(webhook_router, prefix="/webhooks/pipefy", tags=["webhook"])
