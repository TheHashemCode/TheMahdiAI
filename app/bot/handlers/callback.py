from telegram import Update
from telegram.ext import ContextTypes
import logging
from app.core.db import async_session_maker
from app.models.user import User
from sqlmodel import select
from app.core.prompts import LANGUAGE_NAMES

logger = logging.getLogger(__name__)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all button callbacks."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = update.effective_user.id
    
    if data == "lang_custom":
        await query.edit_message_text(
            text="Please type your preferred language manually (e.g., 'Japanese' or 'Italian').\n\n"
                 "*(Silakan ketik bahasa pilihan Anda secara manual, misalnya 'Jepang' atau 'Italia')*"
        )
        context.user_data["awaiting_language"] = True
        return

    if data.startswith("lang_"):
        lang_code = data.split("_")[1]
        lang_display = LANGUAGE_NAMES.get(lang_code, lang_code.upper())
        
        async with async_session_maker() as session:
            stmt = select(User).where(User.telegram_id == user_id)
            result = await session.execute(stmt)
            db_user = result.scalar_one_or_none()
            
            if db_user:
                # Store the code (e.g. 'en') so prompts.py can map it to full name
                db_user.language = lang_code
                await session.commit()
                
        response = (
            f"Language successfully set to **{lang_display}**! ✅\n\n"
            "You can now ask me anything, and I will respond to you thoughtfully."
        )
        
        await query.edit_message_text(text=response, parse_mode="Markdown")
