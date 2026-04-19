from telegram import Update
from telegram.ext import ContextTypes
import logging

logger = logging.getLogger(__name__)

async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for the /language command."""
    if not context.args:
        await update.message.reply_text("Penggunaan: /language [id|en|ar]")
        return
        
    lang_code = context.args[0].lower()
    if lang_code not in ["id", "en", "ar"]:
        await update.message.reply_text("Bahasa tidak didukung. Pilih: id, en, ar.")
        return
        
    # TODO: Update user language preference in PostgreSQL
    
    responses = {
        "id": "Bahasa berhasil diubah ke Bahasa Indonesia.",
        "en": "Language successfully changed to English.",
        "ar": "تم تغيير اللغة بنجاح إلى العربية."
    }
    
    await update.message.reply_text(responses[lang_code])
