"""LLM factory (Groq, free tier).

Modern LangChain entry points:
- ChatGroq from langchain_groq
- both the generator and the (cheaper) evaluator come from the same provider
"""
from langchain_groq import ChatGroq

from config import EVAL_MODEL, GROQ_API_KEY, LLM_MODEL


def get_llm(temperature: float = 0.2) -> ChatGroq:
    """Generator model. Used to produce final answers."""
    return ChatGroq(
        model=LLM_MODEL,
        temperature=temperature,
        max_tokens=1024,
        api_key=GROQ_API_KEY,
    )


def get_eval_llm(temperature: float = 0.0) -> ChatGroq:
    """Cheap evaluator model. Used by the faithfulness/quality scorer."""
    return ChatGroq(
        model=EVAL_MODEL,
        temperature=temperature,
        max_tokens=256,
        api_key=GROQ_API_KEY,
    )
