"""Answer evaluation with RAGAS.

Uses the cheap eval model (Groq llama-3.1-8b-instant) to score a single
answer for faithfulness against the retrieved contexts. Returns a float 0..1.
Runs best-effort: any failure logs a warning and returns 0.0 instead of
breaking the chat.
"""
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("evaluate")


def _make_metrics():
    """Import RAGAS lazily and bind the faithfulness metric to our Groq LLM.

    LangchainLLMWrapper is deprecated in favor of llm_factory, but it's the
    only path that works cleanly with our existing ChatGroq instance. It still
    works fine in RAGAS 0.4.x.
    """
    from ragas.llms import LangchainLLMWrapper
    from ragas.metrics import faithfulness

    from src.llm import get_eval_llm

    faithfulness.llm = LangchainLLMWrapper(get_eval_llm())
    return [faithfulness]


def answer(question: str, answer: str, contexts: list[str]) -> float:
    """Score faithfulness of `answer` given `contexts`. 0..1."""
    try:
        from datasets import Dataset
        from ragas import evaluate as ragas_evaluate

        eval_ds = Dataset.from_dict(
            {
                "question": [question],
                "answer": [answer],
                "contexts": [contexts],
            }
        )
        metrics = _make_metrics()
        result = ragas_evaluate(eval_ds, metrics=metrics)
        value = result["faithfulness"]
        # ragas can return a nested list (one entry per metric/scored unit)
        if isinstance(value, (list, tuple)):
            value = value[0] if value else 0.0
        score = float(value)
        return max(0.0, min(1.0, score))
    except Exception as e:  # pragma: no cover - defensive
        logger.warning("RAGAS evaluation failed: %s", e)
        return 0.0
