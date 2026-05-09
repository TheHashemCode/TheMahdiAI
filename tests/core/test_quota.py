import pytest

from app.core.quota import estimate_tokens, get_truncated_context


def test_estimate_tokens_returns_zero_for_empty_text():
    assert estimate_tokens("") == 0


def test_estimate_tokens_is_reproducible():
    assert estimate_tokens("abcd") == 2  # 4 chars -> 2 tokens by implementation
    assert estimate_tokens("abcdefghi") == 3  # 9 chars -> 3 tokens


@pytest.mark.asyncio
async def test_get_truncated_context_preserves_system_and_recent_messages():
    messages = [
        {"role": "system", "content": "system msg"},
        {"role": "user", "content": "hi"},
        {"role": "assistant", "content": "hij"},
        {"role": "user", "content": "abc"},
    ]

    truncated = await get_truncated_context(messages, max_tokens_limit=5)

    assert truncated[0]["role"] == "system"
    assert truncated == [
        {"role": "system", "content": "system msg"},
        {"role": "assistant", "content": "hij"},
        {"role": "user", "content": "abc"},
    ]


@pytest.mark.asyncio
async def test_get_truncated_context_with_empty_messages():
    assert await get_truncated_context([], max_tokens_limit=10) == []
