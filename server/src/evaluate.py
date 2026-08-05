"""Answer evaluation with RAGAS.

Uses the cheap eval model (Groq llama-3.1-8b-instant) to score a single
answer for faithfulness against the retrieved contexts. Returns a float 0..1.
Runs best-effort: any failure logs a warning and returns 0.0 instead of
breaking the chat.
"""
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("evaluate")


def answer(question: str, answer: str, contexts: list[str]) -> float:
    """Score faithfulness of `answer` given `contexts`. 0..1."""
    try:
        from datasets import Dataset
        from ragas import evaluate as ragas_evaluate
        from ragas.metrics import faithfulness

        eval_ds = Dataset.from_dict(
            {
                "question": [question],
                "answer": [answer],
                "contexts": [contexts],
            }
        )
        result = ragas_evaluate(eval_ds, metrics=[faithfulness])
        score = float(result["faithfulness"])
        return max(0.0, min(1.0, score))
    except Exception as e:  # pragma: no cover - defensive
        logger.warning("RAGAS evaluation failed: %s", e)
        return 0.0