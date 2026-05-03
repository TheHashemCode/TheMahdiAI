import logging
import litellm
import asyncio
from typing import Dict, Any, List, AsyncGenerator, Tuple
from app.core.config import get_settings
from app.core.circuit_breaker import (
    openai_circuit_breaker, 
    anthropic_circuit_breaker, 
    groq_circuit_breaker
)

settings = get_settings()
logger = logging.getLogger(__name__)

# Apply timeout to litellm
litellm.request_timeout = 60


async def call_llm_with_provider(
    provider_name: str, 
    model: str, 
    messages: List[Dict[str, str]], 
    circuit_breaker, 
    api_key: str,
    **kwargs
) -> Dict[str, Any]:
    
    if not circuit_breaker.can_make_request():
        logger.warning(f"Circuit breaker for {provider_name} is OPEN. Skipping.")
        raise Exception(f"Provider {provider_name} is currently unavailable.")
        
    try:
        if not api_key:
            raise ValueError(f"API key for {provider_name} is missing.")
            
        logger.info(f"Attempting to call {provider_name} ({model})")
        
        full_model_name = f"{provider_name}/{model}"
        
        response = await litellm.acompletion(
            model=full_model_name,
            messages=messages,
            api_key=api_key,
            **kwargs
        )
        
        circuit_breaker.record_success()
        return {
            "content": response.choices[0].message.content,
            "provider": provider_name,
            "model": model,
            "usage": dict(response.usage) if hasattr(response, 'usage') else {}
        }
        
    except Exception as e:
        is_circuit_breaker_error = False
        error_str = str(e).lower()
        if "429" in error_str or "500" in error_str or "502" in error_str or "503" in error_str or "timeout" in error_str:
            is_circuit_breaker_error = True
            
        if is_circuit_breaker_error:
            circuit_breaker.record_failure()
            
        logger.error(f"Error calling {provider_name}: {e}")
        raise


async def call_llm_stream(
    provider_name: str,
    model: str,
    messages: List[Dict[str, str]],
    circuit_breaker,
    api_key: str,
    **kwargs
) -> AsyncGenerator[Tuple[str, Dict[str, Any]], None]:
    """Stream LLM response, yielding (chunk_text, metadata) tuples."""
    
    if not circuit_breaker.can_make_request():
        raise Exception(f"Provider {provider_name} is currently unavailable.")
    
    if not api_key:
        raise ValueError(f"API key for {provider_name} is missing.")
    
    logger.info(f"Streaming from {provider_name} ({model})")
    full_model_name = f"{provider_name}/{model}"
    
    try:
        response = await litellm.acompletion(
            model=full_model_name,
            messages=messages,
            api_key=api_key,
            stream=True,
            stream_options={"include_usage": True},
            **kwargs
        )
        
        full_content = ""
        usage_data = {}
        
        async for chunk in response:
            delta = chunk.choices[0].delta
            if delta and delta.content:
                full_content += delta.content
                yield delta.content, {}
            
            # Capture usage from the final chunk
            if hasattr(chunk, 'usage') and chunk.usage:
                usage_data = dict(chunk.usage)
        
        circuit_breaker.record_success()
        
        # Yield final metadata
        yield "", {
            "done": True,
            "provider": provider_name,
            "model": model,
            "content": full_content,
            "usage": usage_data
        }
        
    except Exception as e:
        error_str = str(e).lower()
        if any(code in error_str for code in ["429", "500", "502", "503", "timeout"]):
            circuit_breaker.record_failure()
        logger.error(f"Stream error from {provider_name}: {e}")
        raise


async def generate_response_stream(
    messages: List[Dict[str, str]], **kwargs
) -> AsyncGenerator[Tuple[str, Dict[str, Any]], None]:
    """
    Stream response with 3-level failover.
    Yields (chunk_text, metadata) tuples. Final chunk has metadata["done"]=True.
    """
    
    providers = [
        ("openai", settings.OPENAI_MODEL, openai_circuit_breaker, settings.OPENAI_API_KEY,
         {"api_base": settings.OPENAI_URL} if settings.OPENAI_URL else {}),
        ("anthropic", settings.ANTHROPIC_MODEL, anthropic_circuit_breaker, settings.ANTHROPIC_API_KEY, {}),
        ("groq", settings.GROQ_MODEL, groq_circuit_breaker, settings.GROQ_API_KEY, {}),
    ]
    
    for provider_name, model, cb, api_key, extra_kwargs in providers:
        try:
            merged_kwargs = {**kwargs, **extra_kwargs}
            async for chunk_text, metadata in call_llm_stream(
                provider_name, model, messages, cb, api_key, **merged_kwargs
            ):
                yield chunk_text, metadata
            return  # Success, don't try next provider
        except Exception as e:
            logger.warning(f"Stream failover: {provider_name} failed ({e}). Trying next...")
            continue
    
    # All providers failed
    yield "Sorry, all AI services are currently busy. Please try again in a few moments.", {
        "done": True,
        "error": True,
        "provider": "none",
        "content": "Sorry, all AI services are currently busy.",
        "usage": {}
    }


async def generate_response(messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
    """
    Non-streaming response with 3-level failover (kept for backward compat).
    """
    
    # Provider 1: OpenAI
    try:
        kwargs_openai = {}
        if settings.OPENAI_URL:
            kwargs_openai["api_base"] = settings.OPENAI_URL
            
        return await call_llm_with_provider(
            "openai", 
            settings.OPENAI_MODEL, 
            messages, 
            openai_circuit_breaker,
            settings.OPENAI_API_KEY,
            **kwargs,
            **kwargs_openai
        )
    except Exception as e:
        logger.warning(f"Primary provider (OpenAI) failed. Falling back to Backup 1...")
        
    # Provider 2: Anthropic
    try:
        return await call_llm_with_provider(
            "anthropic", 
            settings.ANTHROPIC_MODEL, 
            messages, 
            anthropic_circuit_breaker,
            settings.ANTHROPIC_API_KEY,
            **kwargs
        )
    except Exception as e:
        logger.warning(f"Backup 1 (Anthropic) failed. Falling back to Backup 2...")
        
    # Provider 3: Groq
    try:
        return await call_llm_with_provider(
            "groq", 
            settings.GROQ_MODEL, 
            messages, 
            groq_circuit_breaker,
            settings.GROQ_API_KEY,
            **kwargs
        )
    except Exception as e:
        logger.error("All AI providers failed!")
        return {
            "error": True,
            "content": "Maaf, seluruh layanan AI sedang sibuk saat ini. Mohon coba beberapa saat lagi.",
            "provider": "none"
        }
