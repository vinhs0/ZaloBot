import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.zalo_bot import build_bot

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

_listen_task: asyncio.Task | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _listen_task
    bot = build_bot()
    _listen_task = asyncio.create_task(asyncio.to_thread(bot.listen))
    logger.info("Zalo bot listener started")
    yield
    if _listen_task:
        _listen_task.cancel()


app = FastAPI(title="Zalo LLM Chatbot", lifespan=lifespan)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
