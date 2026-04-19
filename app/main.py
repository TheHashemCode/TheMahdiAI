from contextlib import asynccontextmanager
from fastapi import FastAPI
import logging
import asyncio

from app.core.config import get_settings
from app.api.v1.router import api_router
from app.bot.bot import create_bot_app

settings = get_settings()

logging.basicConfig(
    level=getattr(logging, settings.APP_LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

bot_app = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global bot_app
    # Startup actions
    logger.info(f"Starting {settings.APP_NAME} in {settings.APP_ENV} mode")
    # TODO: Initialize DB connections
    
    if settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_BOT_TOKEN != "YOUR_BOT_TOKEN_HERE":
        bot_app = create_bot_app()
        await bot_app.initialize()
        if settings.TELEGRAM_WEBHOOK_URL:
            # Webhook mode
            await bot_app.bot.set_webhook(url=settings.TELEGRAM_WEBHOOK_URL, secret_token=settings.TELEGRAM_WEBHOOK_SECRET)
            logger.info("Bot Webhook set.")
        else:
            # Polling mode
            logger.info("Starting bot in polling mode.")
            await bot_app.start()
            await bot_app.updater.start_polling()
            
    yield
    # Shutdown actions
    logger.info(f"Shutting down {settings.APP_NAME}")
    # TODO: Close DB connections
    
    if bot_app:
        if settings.TELEGRAM_WEBHOOK_URL:
            await bot_app.bot.delete_webhook()
        else:
            await bot_app.updater.stop()
        await bot_app.stop()
        await bot_app.shutdown()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Powered Telegram Bot (RAG) Backend",
    lifespan=lifespan,
    docs_url="/docs" if settings.APP_DEBUG else None,
    redoc_url="/redoc" if settings.APP_DEBUG else None,
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "ok", "version": settings.APP_VERSION}
