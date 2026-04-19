from telegram import Update
from telegram.ext import ContextTypes
import logging
from app.core.db import async_session_maker
from app.models.user import User
from sqlmodel import select

logger = logging.getLogger(__name__)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all button callbacks."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = update.effective_user.id
    
    if data.startswith("lang_"):
        lang_code = data.split("_")[1]
        
        async with async_session_maker() as session:
            stmt = select(User).where(User.telegram_id == user_id)
            result = await session.execute(stmt)
            db_user = result.scalar_one_or_none()
            
            if db_user:
                db_user.language = lang_code
                await session.commit()
                
        responses = {
            "id": "Bahasa berhasil diatur ke Bahasa Indonesia! 🇮🇩\nSilakan bebas bertanya apapun, saya akan merespon menggunakan kapabilitas AI saya.",
            "en": "Language successfully set to English! 🇬🇧\nFeel free to ask anything, I will respond using my AI capabilities.",
            "ar": "تم ضبط اللغة بنجاح على العربية! 🇸🇦\nلا تتردد في طرح أي سؤال، وسأرد باستخدام إمكانيات الذكاء الاصطناعي الخاصة بي."
        }
        
        await query.edit_message_text(text=responses.get(lang_code, responses["id"]))
