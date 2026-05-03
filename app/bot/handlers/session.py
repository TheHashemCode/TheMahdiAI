from datetime import datetime, timezone
from telegram import Update
from telegram.ext import ContextTypes
import logging
from sqlmodel import select
from app.core.db import async_session_maker
from app.models.user import User
from app.models.session import ChatSession

logger = logging.getLogger(__name__)

async def new_session_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for the /new_session command — closes active session and creates a new one."""
    tg_user = update.effective_user

    async with async_session_maker() as db_session:
        # Find user
        stmt = select(User).where(User.telegram_id == tg_user.id)
        result = await db_session.execute(stmt)
        db_user = result.scalar_one_or_none()

        if not db_user:
            await update.message.reply_text("Please type /start first.")
            return

        # Close all active sessions
        stmt = select(ChatSession).where(
            ChatSession.user_id == db_user.id,
            ChatSession.is_active == True
        )
        result = await db_session.execute(stmt)
        active_sessions = result.scalars().all()

        for s in active_sessions:
            s.is_active = False
            s.closed_at = datetime.now(timezone.utc)

        # Create fresh session
        new_session = ChatSession(
            user_id=db_user.id,
            is_active=True,
            context_window=[]
        )
        db_session.add(new_session)
        await db_session.commit()

    logger.info(f"User {tg_user.id} started a new session.")
    await update.message.reply_text(
        "✨ New conversation session started.\n"
        "Previous context has been cleared from my memory.\n\n"
        "Feel free to ask me anything!"
    )
