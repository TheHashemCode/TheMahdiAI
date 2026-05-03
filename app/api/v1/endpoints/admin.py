from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
import uuid

from app.core.db import get_session
from app.models.user import User
from app.models.session import ChatSession
from app.models.token_log import TokenLog
from app.models.bot_config import BotConfig

router = APIRouter()

@router.get("/stats")
async def get_stats(session: AsyncSession = Depends(get_session)) -> Dict[str, Any]:
    """Get overall statistics for the dashboard."""
    user_count = await session.execute(select(func.count(User.id)))
    session_count = await session.execute(select(func.count(ChatSession.id)))
    token_sum = await session.execute(select(func.sum(TokenLog.total_tokens)))
    
    return {
        "total_users": user_count.scalar() or 0,
        "total_sessions": session_count.scalar() or 0,
        "total_tokens_used": token_sum.scalar() or 0,
    }

@router.get("/users")
async def list_users(session: AsyncSession = Depends(get_session)) -> List[User]:
    """List all registered users."""
    result = await session.execute(select(User).order_by(User.created_at.desc()))
    return result.scalars().all()

@router.get("/sessions")
async def list_sessions(session: AsyncSession = Depends(get_session)) -> List[Dict[str, Any]]:
    """List recent chat sessions with user info."""
    stmt = select(ChatSession, User.username).join(User).order_by(ChatSession.created_at.desc()).limit(50)
    result = await session.execute(stmt)
    sessions = []
    for chat_session, username in result:
        sessions.append({
            **chat_session.model_dump(),
            "username": username
        })
    return sessions

@router.get("/configs")
async def list_configs(session: AsyncSession = Depends(get_session)) -> List[BotConfig]:
    """List all bot configurations."""
    result = await session.execute(select(BotConfig))
    return result.scalars().all()

ALLOWED_CONFIG_KEYS = [
    "system_prompt",
    "active_notebook_id",
    "notebook_fallback_chain",
    "fallback_min_refs",
    "max_daily_tokens",
    "max_req_per_minute"
]

@router.post("/configs")
async def update_config(config_data: Dict[str, str], session: AsyncSession = Depends(get_session)):
    """Update or create a bot config value."""
    key = config_data.get("key")
    value = config_data.get("value")
    description = config_data.get("description")
    
    if not key or value is None:
        raise HTTPException(status_code=400, detail="Key and value are required")
        
    if key not in ALLOWED_CONFIG_KEYS:
        raise HTTPException(status_code=403, detail=f"Configuration key '{key}' is not allowed to be updated directly.")
        
    stmt = select(BotConfig).where(BotConfig.key == key)
    result = await session.execute(stmt)
    db_config = result.scalar_one_or_none()
    
    if db_config:
        db_config.value = value
        if description is not None:
            db_config.description = description
    else:
        db_config = BotConfig(key=key, value=value, description=description)
        session.add(db_config)
        
    await session.commit()
    return {"status": "success"}
