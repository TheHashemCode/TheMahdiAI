from telegram import Update
from telegram.ext import ContextTypes
import logging
from app.core.ai_gateway import generate_response

logger = logging.getLogger(__name__)

async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for the /search command, leveraging LLM built-in search tools."""
    if not context.args:
        await update.message.reply_text("Penggunaan: /search [pertanyaan/topik]")
        return
        
    query = " ".join(context.args)
    user = update.effective_user
    
    logger.info(f"User {user.id} requested search: {query}")
    
    await update.message.reply_text("Sedang mencari informasi untuk Anda... 🔍")
    
    # We instruct the LLM to search the web to answer this.
    # Note: For true built-in tool usage, litellm supports passing `tools` and `tool_choice`,
    # but some models (e.g., Perplexity or specific GPT/Claude functions) handle it natively 
    # if prompted or configured correctly. For Phase 1, we pass a system prompt encouraging
    # factual lookup.
    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant. Use your available tools or up-to-date knowledge "
                "to answer the user's search query. Provide sources or references if available."
            )
        },
        {
            "role": "user",
            "content": f"Tolong cari informasi tentang: {query}"
        }
    ]
    
    response_data = await generate_response(messages)
    
    if response_data.get("error"):
        await update.message.reply_text(response_data["content"])
    else:
        # TODO: Log tokens used here via response_data["usage"]
        await update.message.reply_text(response_data["content"])
