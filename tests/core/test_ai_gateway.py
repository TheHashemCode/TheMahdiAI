from types import SimpleNamespace

import pytest

from app.core import ai_gateway


class DummyCircuitBreaker:
    def __init__(self, allow_request: bool = True):
        self.allow_request = allow_request
        self.successes = 0
        self.failures = 0

    def can_make_request(self):
        return self.allow_request

    def record_success(self):
        self.successes += 1

    def record_failure(self):
        self.failures += 1


@pytest.mark.asyncio
async def test_call_llm_with_provider_raises_when_api_key_missing(monkeypatch):
    with pytest.raises(ValueError, match="API key for openai is missing"):
        await ai_gateway.call_llm_with_provider(
            "openai",
            "gpt-4o",
            [],
            DummyCircuitBreaker(),
            ""
        )


@pytest.mark.asyncio
async def test_generate_response_falls_back_to_next_provider(monkeypatch):
    openai_cb = DummyCircuitBreaker()
    anthropic_cb = DummyCircuitBreaker()
    groq_cb = DummyCircuitBreaker()

    monkeypatch.setattr(ai_gateway, "openai_circuit_breaker", openai_cb)
    monkeypatch.setattr(ai_gateway, "anthropic_circuit_breaker", anthropic_cb)
    monkeypatch.setattr(ai_gateway, "groq_circuit_breaker", groq_cb)

    monkeypatch.setattr(ai_gateway.settings, "OPENAI_API_KEY", "openai")
    monkeypatch.setattr(ai_gateway.settings, "ANTHROPIC_API_KEY", "anthropic")
    monkeypatch.setattr(ai_gateway.settings, "GROQ_API_KEY", "groq")

    async def fake_acompletion(model, **kwargs):
        if model.startswith("openai/"):
            raise Exception("500 internal")
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="fallback ok"))],
            usage={"prompt_tokens": 10, "completion_tokens": 4, "total_tokens": 14},
        )

    monkeypatch.setattr(ai_gateway.litellm, "acompletion", fake_acompletion)

    response = await ai_gateway.generate_response([{"role": "user", "content": "hello"}])

    assert response["provider"] == "anthropic"
    assert response["content"] == "fallback ok"
    assert anthropic_cb.successes == 1
    assert openai_cb.failures == 1


@pytest.mark.asyncio
async def test_generate_response_stream_returns_done_metadata(monkeypatch):
    openai_cb = DummyCircuitBreaker()
    monkeypatch.setattr(ai_gateway, "openai_circuit_breaker", openai_cb)
    monkeypatch.setattr(ai_gateway, "anthropic_circuit_breaker", DummyCircuitBreaker())
    monkeypatch.setattr(ai_gateway, "groq_circuit_breaker", DummyCircuitBreaker())

    monkeypatch.setattr(ai_gateway.settings, "OPENAI_API_KEY", "openai")
    monkeypatch.setattr(ai_gateway.settings, "OPENAI_URL", None)
    monkeypatch.setattr(ai_gateway.settings, "OPENAI_MODEL", "gpt-4o")

    async def fake_acompletion(*, model, **kwargs):
        if model != "openai/gpt-4o":
            raise AssertionError("Unexpected model")

        async def _stream():
            yield SimpleNamespace(
                choices=[SimpleNamespace(delta=SimpleNamespace(content="part 1"))],
                usage=None,
            )
            yield SimpleNamespace(
                choices=[SimpleNamespace(delta=SimpleNamespace(content=" part 2"))],
                usage={"total_tokens": 7},
            )

        return _stream()

    monkeypatch.setattr(ai_gateway.litellm, "acompletion", fake_acompletion)

    chunks = []
    async for chunk, metadata in ai_gateway.generate_response_stream(
        [{"role": "user", "content": "hello"}],
    ):
        chunks.append((chunk, metadata))

    assert chunks[-1][1]["done"] is True
    assert chunks[-1][1]["provider"] == "openai"
    assert chunks[-1][1]["content"] == "part 1 part 2"
    assert openai_cb.successes == 1
