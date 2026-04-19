import logging
import time
from datetime import datetime, timedelta
from typing import Optional, Tuple
from redis.asyncio import Redis, from_url
from sqlmodel import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import get_settings
from app.models.token_log import TokenLog
from app.models.user import User

settings = get_settings()
logger = logging.getLogger(__name__)

_redis: Optional[Redis] = None

async def get_redis() -> Optional[Redis]:
    global _redis
    if not settings.REDIS_URL:
        return None
    if _redis is None:
        try:
            _redis = from_url(settings.REDIS_URL, decode_responses=True)
            # Test connection
            await _redis.ping()
        except Exception as e:
            logger.warning(f"Failed to connect to Redis: {e}. Falling back to DB for quotas.")
            _redis = None
    return _redis

class QuotaManager:
    """Manages rate limits and daily quotas using Redis (primary) or DB (fallback)."""
    
    def __init__(self, redis: Optional[Redis] = None):
        self.redis = redis

    async def check_rate_limit(self, user_id: int, db_user_id: str, db_session: AsyncSession, max_per_min: int) -> Tuple[bool, int]:
        """Check requests per minute."""
        if self.redis:
            try:
                key = f"ratelimit:min:{user_id}"
                count = await self.redis.incr(key)
                if count == 1:
                    await self.redis.expire(key, 60)
                return count <= max_per_min, count
            except Exception as e:
                logger.error(f"Redis Ratelimit Error: {e}")
        
        # Fallback to DB
        one_min_ago = datetime.utcnow() - timedelta(minutes=1)
        stmt = select(func.count(TokenLog.id)).where(
            TokenLog.user_id == db_user_id,
            TokenLog.created_at >= one_min_ago
        )
        result = await db_session.execute(stmt)
        count = result.scalar() or 0
        return count < max_per_min, count + 1

    async def check_daily_quota(self, user_id: int, db_user_id: str, db_session: AsyncSession, max_reqs: int) -> Tuple[bool, int]:
        """Check requests per day."""
        if self.redis:
            try:
                key = f"quota:day:req:{user_id}"
                count = await self.redis.incr(key)
                if count == 1:
                    await self.redis.expire(key, 86400)
                return count <= max_reqs, count
            except Exception as e:
                logger.error(f"Redis Quota Error: {e}")

        # Fallback to DB
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        stmt = select(func.count(TokenLog.id)).where(
            TokenLog.user_id == db_user_id,
            TokenLog.created_at >= today_start
        )
        result = await db_session.execute(stmt)
        count = result.scalar() or 0
        return count < max_reqs, count + 1

    async def check_token_quota(self, user_id: int, db_user: User, max_tokens: int) -> Tuple[bool, int]:
        """
        Layered check:
        1. Check Redis (Layer 1).
        2. If Redis is empty, hydrate from DB User.daily_token_used (Layer 2).
        3. Return comparison.
        """
        if self.redis:
            try:
                key = f"quota:day:tokens:{user_id}"
                current = await self.redis.get(key)
                
                if current is None:
                    # Hydrate Layer 1 from Layer 2 (DB)
                    val = db_user.daily_token_used
                    await self.redis.set(key, val)
                    await self.redis.expire(key, 86400)
                else:
                    val = int(current)
                
                return val < max_tokens, val
            except Exception as e:
                logger.error(f"Redis Token Quota Error: {e}")

        # Static Fallback to DB
        return db_user.daily_token_used < max_tokens, db_user.daily_token_used

    async def log_token_usage(self, user_id: int, tokens: int):
        """Update daily token counter in Redis if available."""
        if not self.redis:
            return
        try:
            key = f"quota:day:tokens:{user_id}"
            await self.redis.incrby(key, tokens)
            await self.redis.expire(key, 86400, nx=True)
        except Exception:
            pass

def estimate_tokens(text: str) -> int:
    """Rough estimation of tokens (~4 chars per token)."""
    if not text: return 0
    return len(text) // 4 + 1

async def get_truncated_context(messages: list, max_tokens_limit: int) -> list:
    """
    Truncates message history to fit within a specific token limit.
    Always preserves the system message.
    """
    if not messages: return []
    
    system_msg = messages[0] if messages[0]['role'] == 'system' else None
    chat_msgs = messages[1:] if system_msg else messages
    
    current_tokens = estimate_tokens(system_msg['content']) if system_msg else 0
    final_msgs = []
    
    # Iterate backwards to keep the most recent messages
    for msg in reversed(chat_msgs):
        msg_tokens = estimate_tokens(msg['content'])
        if current_tokens + msg_tokens <= max_tokens_limit:
            final_msgs.insert(0, msg)
            current_tokens += msg_tokens
        else:
            break
            
    if system_msg:
        final_msgs.insert(0, system_msg)
        
    return final_msgs
