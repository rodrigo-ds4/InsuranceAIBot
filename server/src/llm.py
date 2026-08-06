"""LLM factory with multi-provider failover.

Primary: Groq (free tier). Fallback: OpenRouter (OpenAI-compatible API).
If the primary is rate-limited (429) or over capacity (503), we transparently
fall back to the next provider so RAG turns and evaluations keep working.
"""
import time
from functools import lru_cache

from langchain_core.language_models.chat_models import BaseChatModel

from config import (
    EVAL_MODEL,
    GROQ_API_KEY,
    LLM_MODEL,
    OPENROUTER_API_KEY,
    OPENROUTER_BASE_URL,
    OPENROUTER_MODEL,
)

_MAX_RETRIES = 3
_BASE_DELAY = 2.0  # seconds


class _TransientError(Exception):
    """Raised to signal that a provider is rate-limited / over capacity."""


def _is_transient(exc: Exception) -> bool:
    code = getattr(exc, "status_code", None)
    if code is None:
        code = getattr(getattr(exc, "response", None), "status_code", None)
    return code in (429, 502, 503)


def _groq(model: str, temperature: float, max_tokens: int) -> BaseChatModel:
    from langchain_groq import ChatGroq

    return ChatGroq(
        model=model, temperature=temperature, max_tokens=max_tokens, api_key=GROQ_API_KEY
    )


def _openrouter(model: str, temperature: float, max_tokens: int) -> BaseChatModel:
    from langchain_openai import ChatOpenAI

    return ChatOpenAI(
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        api_key=OPENROUTER_API_KEY,
        base_url=OPENROUTER_BASE_URL,
    )


class FailoverChatModel(BaseChatModel):
    """Attempts each provider in order (Groq → OpenRouter), with backoff.

    Only transient errors (429/5xx) trigger a switch; real failures propagate.
    """

    temperature: float = 0.2
    max_tokens: int = 1024

    @property
    def _llm_type(self) -> str:
        return "failover"

    def _build_chain(self) -> list[BaseChatModel]:
        chain = []
        if GROQ_API_KEY:
            chain.append(_groq(LLM_MODEL, self.temperature, self.max_tokens))
        if OPENROUTER_API_KEY:
            chain.append(_openrouter(OPENROUTER_MODEL, self.temperature, self.max_tokens))
        if not chain:
            raise RuntimeError("No LLM provider configured (set GROQ_API_KEY or OPENROUTER_API_KEY).")
        return chain

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        last_error: Exception | None = None
        for provider in self._build_chain():
            for attempt in range(_MAX_RETRIES):
                try:
                    return provider._generate(
                        messages, stop=stop, run_manager=run_manager, **kwargs
                    )
                except Exception as exc:  # noqa: BLE001 - classify and route
                    last_error = exc
                    transient = _is_transient(exc)
                    if attempt == _MAX_RETRIES - 1 or not transient:
                        break  # exhausted retries: try next provider (or raise)
                    time.sleep(_BASE_DELAY * (2**attempt))
        raise RuntimeError(f"All LLM providers failed: {type(last_error).__name__}: {last_error}")


@lru_cache(maxsize=8)
def get_llm(temperature: float = 0.2) -> BaseChatModel:
    """Generator (main) model with Groq→OpenRouter failover."""
    return FailoverChatModel(temperature=temperature, max_tokens=1024)


@lru_cache(maxsize=4)
def get_eval_llm(temperature: float = 0.0) -> BaseChatModel:
    """Cheap evaluator with failover. RAGAS needs generous output tokens."""
    return FailoverChatModel(temperature=temperature, max_tokens=2048)