"""RAG chain: the single entry point the server calls.

The previous linear pipeline (retrieve -> build prompt -> generate) is now
delegated to a ReAct agent (see src.agent.py) that decides *when* to retrieve
policy clauses (buscar_poliza) and *when* to recall user memory
(buscar_memoria), then answers grounded on the tool output.

Flow per incoming message:
1. guardrail check on the raw input
2. run the ReAct reasoning loop (tools: buscar_poliza, buscar_memoria)
3. persist the exchange to short & long term memory
4. optionally score the answer for faithfulness (see src/evaluate.py)
"""
from src.agent import ask as _react_ask
from src.guardrails import GuardrailsError, check_input


def ask(
    question: str,
    retriever,
    short_memory,
    user_id: str = "default",
    evaluate_answer: bool = False,
) -> tuple[str, float]:
    """Run one full turn. Returns (answer, faithfulness_score).

    - retriever: kept for backwards compatibility with the server entry point;
      the agent reaches the store through its buscar_poliza tool.
    - short_memory: in-memory short-term buffer.
    - evaluate_answer: when True, scores faithfulness with RAGAS.
    """
    # 1. guardrails (raw input)
    check_input(question)

    # 2. ReAct agent turn (retrieval + generation)
    return _react_ask(
        question=question,
        retriever=retriever,
        short_memory=short_memory,
        user_id=user_id,
        evaluate_answer=evaluate_answer,
    )


__all__ = ["ask", "GuardrailsError"]
