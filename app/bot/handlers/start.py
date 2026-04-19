from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import logging
from app.core.db import async_session_maker
from app.models.user import User
from sqlmodel import select

logger = logging.getLogger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for the /start command."""
    user = update.effective_user
    logger.info(f"User {user.id} ({user.username}) started the bot.")
    
    # Save or update user in DB
    async with async_session_maker() as session:
        query = select(User).where(User.telegram_id == user.id)
        result = await session.execute(query)
        db_user = result.scalar_one_or_none()
        
        if not db_user:
            db_user = User(
                telegram_id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                language="id" # default
            )
            session.add(db_user)
            await session.commit()
    
    welcome_message = (
        f"Assalamu'alaikum {user.first_name}! 👋\n\n"
        "Saya adalah TheMahdiAI. Silakan pilih bahasa preferensi Anda di bawah ini:\n"
        "*(Please select your preferred language below):*"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("🇮🇩 Indonesia", callback_data="lang_id"),
            InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
            InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_ar")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_message, reply_markup=reply_markup, parse_mode="Markdown")
