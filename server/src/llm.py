"""LLM factory (Groq, free tier).

Modern LangChain entry points:
- ChatGroq from langchain_groq
- both the generator and the (cheaper) evaluator come from the same provider
"""
import time
from functools import lru_cache

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_groq import ChatGroq

from config import EVAL_MODEL, GROQ_API_KEY, LLM_MODEL

_MAX_RETRIES = 4
_BASE_DELAY = 2.0  # seconds


class GroqRetry(ChatGroq):
    """ChatGroq with exponential backoff for 429/503 transient errors.

    The Groq free tier often returns 503 (over capacity) on the big models;
    we retry with jittered backoff instead of failing the whole turn.
    """

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        for attempt in range(_MAX_RETRIES):
            try:
                return super()._generate(messages, stop=stop, run_manager=run_manager, **kwargs)
            except Exception as exc:  # noqa: BLE001 - retry transient API errors
                code = getattr(exc, "status_code", None) or getattr(getattr(exc, "response", None), "status_code", None)
                if code not in (429, 503) or attempt == _MAX_RETRIES - 1:
                    raise
                delay = _BASE_DELAY * (2**attempt) + (attempt * 0.5)
                time.sleep(delay)


def _make(model: str, temperature: float, max_tokens: int) -> BaseChatModel:
    return GroqRetry(
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        api_key=GROQ_API_KEY,
    )


@lru_cache(maxsize=2)
def get_llm(temperature: float = 0.2) -> BaseChatModel:
    """Generator model. Used to produce final answers."""
    return _make(LLM_MODEL, temperature, max_tokens=1024)


@lru_cache(maxsize=1)
def get_eval_llm(temperature: float = 0.0) -> BaseChatModel:
    """Cheap evaluator model. Used by the faithfulness/quality scorer.

    RAGAS needs generous output tokens for structured JSON (its faithfulness
    steps ask the model to enumerate statements + verdicts).
    """
    return _make(EVAL_MODEL, temperature, max_tokens=2048)
