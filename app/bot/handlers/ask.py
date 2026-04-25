import json
from telegram import Update
from telegram.ext import ContextTypes
import logging
from sqlmodel import select
from app.core.db import async_session_maker
from app.models.bot_config import BotConfig
from app.models.user import User
from app.services.notebook_service import notebook_service

logger = logging.getLogger(__name__)

async def ask_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for the /ask command, querying the configured NotebookLM with fallback support."""
    if not context.args:
        await update.message.reply_text("Usage: /ask [your question]")
        return
        
    query = " ".join(context.args)
    user_tg = update.effective_user
    
    # Get configuration and user info
    fallback_chain = []
    fallback_min_refs = 2
    user_id = None
    
    async with async_session_maker() as session:
        # Get internal user id
        user_stmt = select(User).where(User.telegram_id == user_tg.id)
        user_result = await session.execute(user_stmt)
        user_db = user_result.scalar_one_or_none()
        user_id = str(user_db.id) if user_db else None

        # Attempt to get fallback chain
        statement_chain = select(BotConfig).where(BotConfig.key == "notebook_fallback_chain")
        chain_result = await session.execute(statement_chain)
        config_chain = chain_result.scalar_one_or_none()
        
        if config_chain and config_chain.value:
            try:
                fallback_chain = json.loads(config_chain.value)
            except json.JSONDecodeError:
                pass
                
        # Get min refs setting
        statement_min_refs = select(BotConfig).where(BotConfig.key == "fallback_min_refs")
        min_refs_result = await session.execute(statement_min_refs)
        config_min_refs = min_refs_result.scalar_one_or_none()
        if config_min_refs and config_min_refs.value:
            try:
                fallback_min_refs = int(config_min_refs.value)
            except ValueError:
                pass

        # If no chain, fallback to single active notebook for backward compatibility
        if not fallback_chain:
            statement_active = select(BotConfig).where(BotConfig.key == "active_notebook_id")
            active_result = await session.execute(statement_active)
            config_active = active_result.scalar_one_or_none()
            if config_active and config_active.value:
                fallback_chain = [config_active.value]

    if not fallback_chain:
        await update.message.reply_text(
            "⚠️ No active notebook configured. Please configure the Telegram Fallback Chain in the admin dashboard."
        )
        return

    # Cap at 5 notebooks to avoid infinite loops or massive latency
    fallback_chain = fallback_chain[:5]

    msg = await update.message.reply_text("Thinking... 🧠")
    
    try:
        best_response = None
        
        for i, nb_id in enumerate(fallback_chain):
            if i > 0:
                await msg.edit_text(f"Not enough references found. Searching deeper (Level {i+1})... 🧠")
                
            response_data = await notebook_service.ask_question(
                nb_id,
                query,
                user_id=user_id,
                source="telegram"
            )
            
            references = response_data.get("references", [])
            best_response = response_data
            
            # If we found enough references, or if this is the last notebook in the chain, we stop.
            if len(references) >= fallback_min_refs:
                break
                
        answer = best_response.get("answer", "")

        # Telegram has a 4096 character limit
        if len(answer) > 4000:
            # Delete "thinking" message
            await msg.delete()
            for i in range(0, len(answer), 4000):
                await update.message.reply_text(answer[i:i+4000])
        else:
            await msg.edit_text(answer)
            
    except Exception as e:
        logger.error(f"Error in /ask: {e}")
        await msg.edit_text(f"❌ Error querying NotebookLM: {str(e)}")

