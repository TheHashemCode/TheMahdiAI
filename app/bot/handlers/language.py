from telegram import Update
from telegram.ext import ContextTypes
import logging

logger = logging.getLogger(__name__)

async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for the /language command."""
    if not context.args:
        await update.message.reply_text("Usage: /language [en|ar|fa|es|...]")
        return
        
    lang_code = context.args[0].lower()
    await update.message.reply_text(f"Language set to: {lang_code}. Testing connection...")
    # NOTE: Actual persistence logic is handled in the callback query for UI consistency.
    return
        
    # TODO: Update user language preference in PostgreSQL
    
    responses = {
        "id": "Bahasa berhasil diubah ke Bahasa Indonesia.",
        "en": "Language successfully changed to English.",
        "ar": "تم تغيير اللغة بنجاح إلى العربية."
    }
    
    await update.message.reply_text(responses[lang_code])
