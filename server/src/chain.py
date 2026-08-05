"""RAG chain: the single entry point the server calls.

Flow per incoming message:
1. guardrail check on the raw input
2. retrieve documents from the policy store
3. recall long-term memory + short-term turns
4. build the (injection-resilient) prompt
5. call the Groq LLM
6. persist the exchange to short & long term memory
7. optionally score the answer for faithfulness (see src/evaluate.py)
"""
from config import TOP_K
from src import evaluate
from src.guardrails import GuardrailsError, check_input
from src.llm import get_llm
from src.memory.longterm import recall, remember
from src.memory.shortterm import ShortTermMemory
from src.prompt import build_messages


def _extract_context(docs) -> str:
    """Join retrieved documents into a single text block."""
    parts = []
    for d in docs:
        source = d.metadata.get("source", "policy")
        parts.append(f"[{source}]\n{d.page_content}")
    return "\n\n".join(parts)


def _detect_language(question: str) -> str:
    # keep it simple: heuristics-free, defer to model via a prompt line
    return "auto"


def ask(
    question: str,
    retriever,
    short_memory: ShortTermMemory,
    user_id: str = "default",
    evaluate_answer: bool = False,
) -> tuple[str, float]:
    """Run one full turn. Returns (answer, faithfulness_score).

    - retriever: LangChain retriever backed by the policy Chroma store.
    - short_memory: in-memory short-term buffer.
    - evaluate_answer: when True, scores faithfulness with RAGAS.
    """
    # 1. guardrails
    clean_q = check_input(question)

    # 2. retrieval
    docs = retriever.invoke(clean_q)
    context = _extract_context(docs)

    # 3. memory
    long_mem = "\n\n".join(
        d.page_content for d in recall(user_id, clean_q)
    )

    # 4. prompt
    messages = build_messages(
        question=clean_q,
        context=context,
        short_memory=short_memory.to_text(),
        long_memory=long_mem,
        language=_detect_language(clean_q),
    )

    # 5. generate
    llm = get_llm()
    answer = llm.invoke(messages).content

    # 6. persist memory
    short_memory.add(clean_q, answer)
    remember(user_id, clean_q, answer)

    # 7. evaluation (optional)
    score = 0.0
    if evaluate_answer:
        score = evaluate.answer(
            question=clean_q,
            answer=answer,
            contexts=[d.page_content for d in docs],
        )

    return answer, score
