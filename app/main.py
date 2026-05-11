"""
Sanos y Salvos — Notifications Microservice
Handles real-time notifications via WebSocket and event processing.
"""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.events.consumer import start_consumer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("notifications-service")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🔔 Notifications Microservice starting...")
    asyncio.create_task(start_consumer())
    yield
    logger.info("🛑 Notifications Microservice shutting down...")


app = FastAPI(
    title="Sanos y Salvos — Notificaciones",
    description="Microservicio de notificaciones en tiempo real con WebSocket",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/health")
def health():
    return {"status": "healthy", "service": "notifications-service"}
