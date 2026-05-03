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
                language="en" # switch default to english for global reach
            )
            session.add(db_user)
            await session.commit()
    
    welcome_message = (
        f"Assalamu'alaikum {user.first_name}! 👋\n\n"
        "Welcome to **TheMahdiAI**. Please select your preferred language below:\n"
        "*(Silakan pilih bahasa preferensi Anda di bawah ini):*"
    )
    
    # Priority row
    keyboard = [
        [
            InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
            InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_ar"),
            InlineKeyboardButton("🇮🇷 Persian", callback_data="lang_fa"),
            InlineKeyboardButton("🇪🇸 Spanish", callback_data="lang_es"),
        ],
        # Second priority / large groups
        [
            InlineKeyboardButton("🇲🇾 Malaysia", callback_data="lang_ms"),
            InlineKeyboardButton("🇮🇩 Indonesia", callback_data="lang_id"),
            InlineKeyboardButton("🇳🇱 Dutch", callback_data="lang_nl"),
            InlineKeyboardButton("🇰🇷 Korean", callback_data="lang_ko"),
        ],
        # Third row
        [
            InlineKeyboardButton("🇹🇷 Turkish", callback_data="lang_tr"),
            InlineKeyboardButton("🇩🇪 German", callback_data="lang_de"),
            InlineKeyboardButton("🇦🇿 Azerbaijani", callback_data="lang_az"),
            InlineKeyboardButton("🇫🇷 French", callback_data="lang_fr"),
        ],
        # Fourth row
        [
            InlineKeyboardButton("🇵🇱 Polish", callback_data="lang_pl"),
            InlineKeyboardButton("🇵🇰 Urdu", callback_data="lang_ur"),
            InlineKeyboardButton("🇨🇳 Mandarin", callback_data="lang_zh"),
            InlineKeyboardButton("🇮🇱 Hebrew", callback_data="lang_he"),
        ],
        # Custom option
        [
            InlineKeyboardButton("✨ Other (Type manually)", callback_data="lang_custom")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_message, reply_markup=reply_markup, parse_mode="Markdown")
