import time
from telegram import Update
from telegram.ext import ContextTypes
import logging
from sqlmodel import select
from app.core.db import async_session_maker
from app.core.ai_gateway import generate_response_stream
from app.core.prompts import DEFAULT_SYSTEM_PROMPT, LANGUAGE_NAMES
from app.models.user import User
from app.models.session import ChatSession
from app.models.token_log import TokenLog
from app.models.bot_config import BotConfig

logger = logging.getLogger(__name__)

MAX_CONTEXT_MESSAGES = 20
STREAM_EDIT_INTERVAL = 1.0  # Edit message every N seconds
CURSOR = "▍"


async def _get_system_prompt(session) -> str:
    """Fetch admin-configured system prompt, fallback to default."""
    stmt = select(BotConfig).where(BotConfig.key == "system_prompt")
    result = await session.execute(stmt)
    config = result.scalar_one_or_none()
    if config and config.value:
        return config.value
    return DEFAULT_SYSTEM_PROMPT


async def _get_or_create_session(db_session, user_id) -> ChatSession:
    """Get active chat session or create a new one."""
    stmt = select(ChatSession).where(
        ChatSession.user_id == user_id,
        ChatSession.is_active == True
    )
    result = await db_session.execute(stmt)
    chat_session = result.scalar_one_or_none()

    if not chat_session:
        chat_session = ChatSession(
            user_id=user_id,
            is_active=True,
            context_window=[]
        )
        db_session.add(chat_session)
        await db_session.commit()
        await db_session.refresh(chat_session)

    return chat_session


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming text messages with streaming AI response."""
    if not update.message or not update.message.text:
        return

    user_text = update.message.text
    tg_user = update.effective_user

    logger.info(f"Received message from {tg_user.id}: {user_text[:80]}")

    async with async_session_maker() as db_session:
        # 1. Get user from DB
        stmt = select(User).where(User.telegram_id == tg_user.id)
        result = await db_session.execute(stmt)
        db_user = result.scalar_one_or_none()

        if not db_user:
            db_user = User(
                telegram_id=tg_user.id,
                username=tg_user.username,
                first_name=tg_user.first_name,
                last_name=tg_user.last_name,
                language="id"
            )
            db_session.add(db_user)
            await db_session.commit()
            await db_session.refresh(db_user)

        # 2. Get or create active chat session
        chat_session = await _get_or_create_session(db_session, db_user.id)

        # 3. Build system prompt with user context
        system_prompt_template = await _get_system_prompt(db_session)
        user_display_name = db_user.first_name or tg_user.first_name or "User"
        lang_name = LANGUAGE_NAMES.get(db_user.language, "Bahasa Indonesia")

        system_prompt = system_prompt_template.format(
            user_name=user_display_name,
            user_language=lang_name
        )

        # 4. Build messages array with context window
        messages = [{"role": "system", "content": system_prompt}]
        context_window = chat_session.context_window or []
        for msg in context_window[-MAX_CONTEXT_MESSAGES:]:
            messages.append(msg)
        messages.append({"role": "user", "content": user_text})

        # 5. Send initial placeholder message
        sent_msg = await update.message.reply_text(f"{CURSOR}")
        
        # 6. Stream AI response and edit message progressively
        full_response = ""
        last_edit_time = time.time()
        last_edited_text = ""
        final_metadata = {}

        try:
            async for chunk_text, metadata in generate_response_stream(messages):
                if metadata.get("done"):
                    final_metadata = metadata
                    break
                
                full_response += chunk_text
                
                # Throttle edits to avoid Telegram rate limits
                now = time.time()
                if now - last_edit_time >= STREAM_EDIT_INTERVAL and full_response != last_edited_text:
                    try:
                        display_text = full_response + CURSOR
                        if len(display_text) > 4000:
                            display_text = display_text[-4000:]
                        await sent_msg.edit_text(display_text)
                        last_edited_text = full_response
                        last_edit_time = now
                    except Exception as edit_err:
                        # Telegram may throw "message not modified" — safe to ignore
                        logger.debug(f"Edit throttle skip: {edit_err}")

            # 7. Final edit — remove cursor, show complete response
            final_text = final_metadata.get("content", full_response) or full_response
            if final_text:
                if len(final_text) > 4000:
                    # Split long messages
                    await sent_msg.edit_text(final_text[:4000])
                    remaining = final_text[4000:]
                    while remaining:
                        chunk = remaining[:4000]
                        remaining = remaining[4000:]
                        await update.message.reply_text(chunk)
                else:
                    await sent_msg.edit_text(final_text)
            
            # 8. Update session context window
            is_error = final_metadata.get("error", False)
            if not is_error and final_text:
                context_window.append({"role": "user", "content": user_text})
                context_window.append({"role": "assistant", "content": final_text})

                if len(context_window) > MAX_CONTEXT_MESSAGES:
                    context_window = context_window[-MAX_CONTEXT_MESSAGES:]

                chat_session.context_window = context_window

                usage = final_metadata.get("usage", {})
                total_tokens = usage.get("total_tokens", 0)
                chat_session.total_tokens += total_tokens

                from sqlalchemy.orm.attributes import flag_modified
                flag_modified(chat_session, "context_window")
                await db_session.commit()

                # 9. Log token usage
                if total_tokens > 0:
                    provider = final_metadata.get("provider", "unknown")
                    model = final_metadata.get("model", "unknown")
                    is_failover = provider != "openai"

                    token_log = TokenLog(
                        user_id=db_user.id,
                        session_id=chat_session.id,
                        provider=provider,
                        model_name=model,
                        prompt_tokens=usage.get("prompt_tokens", 0),
                        completion_tokens=usage.get("completion_tokens", 0),
                        total_tokens=total_tokens,
                        is_failover=is_failover,
                        failover_reason=f"Fallback to {provider}" if is_failover else None
                    )
                    db_session.add(token_log)
                    db_user.daily_token_used += total_tokens
                    await db_session.commit()

        except Exception as e:
            logger.error(f"Error during streaming: {e}", exc_info=True)
            try:
                await sent_msg.edit_text(
                    "Maaf, terjadi kesalahan saat memproses pesan Anda. Silakan coba lagi."
                )
            except Exception:
                pass
