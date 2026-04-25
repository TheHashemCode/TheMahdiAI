from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from app.core.config import get_settings
from app.bot.handlers.start import start_command
from app.bot.handlers.language import language_command
from app.bot.handlers.session import new_session_command
from app.bot.handlers.search import search_command
from app.bot.handlers.ask import ask_command
from app.bot.handlers.callback import button_callback
from app.bot.handlers.message import handle_message

settings = get_settings()

def create_bot_app():
    """Create and configure the Telegram Bot application."""
    if not settings.TELEGRAM_BOT_TOKEN or settings.TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        raise ValueError("TELEGRAM_BOT_TOKEN is not set.")
        
    application = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).concurrent_updates(True).build()
    
    # Register handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("language", language_command))
    application.add_handler(CommandHandler("new_session", new_session_command))
    application.add_handler(CommandHandler("search", search_command))
    application.add_handler(CommandHandler("ask", ask_command))
    
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message, block=False))
    
    return application
