"""ReAct agent with two tools: buscar_poliza and buscar_memoria.

The reasoning loop follows the classic ReAct pattern — the model iterates over
``Thought / Action / Action Input`` steps and reads back an ``Observation``
until it can emit a final answer. It is implemented manually (rather than via
langgraph's tool-calling agent) because our LLM is a custom failover wrapper
that does not reliably forward bound tools to a provider, so a text-based
ReAct trace works with any chat model.

Available tools
---------------
- buscar_poliza(query, [source]): retrieves relevant policy clauses from the
  persistent Chroma store (document retrieval).
- buscar_memoria(query, user_id): recalls the user's long-term memory facts.

All guardrails still apply at the entry point (see src.chain).
"""
import json
import re

from src.guardrails import check_input
from src.llm import get_llm
from src.memory.longterm import recall, remember
from src.prompt import SYSTEM_PROMPT

_MAX_STEPS = 6

_ActionRe = re.compile(r"\s*Action:\s*(\w+)\s*\(\s*(.*?)\s*\)\s*$", re.S)
_FinalRe = re.compile(r"Final Answer:\s*(.*)", re.S)


def buscar_poliza(query: str, source: str | None = None) -> str:
    """Retrieve policy clauses relevant to the query from the vector store.

    `source` limits the search to a single policy document (a PDF filename
    like "POL320210210.pdf"); when omitted, all indexed policies are searched.
    Returns a text block of the top matches (one per retrieved clause).
    """
    from src.vectorstore import get_policy_retriever

    docs = get_policy_retriever(source=source or None).invoke(query)
    if not docs:
        return "[policy store] no matching clauses retrieved."
    parts = []
    for d in docs:
        src = d.metadata.get("source", "policy")
        parts.append(f"[{src}]\n{d.page_content}")
    return "\n\n".join(parts)


def buscar_memoria(query: str, user_id: str = "default") -> str:
    """Recall facts the assistant has learned about the user in past sessions."""
    docs = recall(user_id, query)
    if not docs:
        return "[memory] nothing relevant remembered about this user."
    return "\n\n".join(d.page_content for d in docs)


def build_tool_desc() -> str:
    return (
        "You have access to the following tools:\n"
        "- buscar_poliza(query, source=''): retrieve policy clauses from the "
        "insurance document store. Use it for any question about coverage, "
        "exclusions, limits or clauses. `source` is optional (a PDF filename "
        "like \"POL320210210.pdf\").\n"
        "- buscar_memoria(query, user_id='default'): recall what you have "
        "previously learned about the user.\n\n"
        "You MUST reason step by step and, before answering, call the tools "
        "that provide the facts. Respond using EXACTLY this format, one per "
        "line:\n\n"
        "Thought: <your reasoning>\n"
        "Action: buscar_poliza({\"query\": \"<search text>\", \"source\": \"<pdf name or ''>\"})\n\n"
        "Then read the Observation I return. Keep going with more Thought/Action "
        "steps if needed. Once you have enough facts, end with:\n"
        "Final Answer: <answer grounded in the observations>\n\n"
        "Example:\n"
        "Thought: The user asks about emergency hospitalization coverage. I need "
        "the policy clauses.\n"
        "Action: buscar_poliza({\"query\": \"hospitalización de emergencia\", "
        "\"source\": \"POL320210210.pdf\"})\n\n"
        "Ground your answer only on what the tools returned. If a tool returns "
        "nothing, say so clearly — never invent clauses, figures or dates.\n"
    )


def run_reasoning(question: str, short_memory: str = "", user_id: str = "default") -> str:
    """Drive the ReAct loop: model proposes an action, we execute it, feed the
    observation back until a final answer is produced or steps run out."""
    system = SYSTEM_PROMPT + "\n\n" + build_tool_desc()
    turn_log: list[tuple[str, str]] = []

    for _ in range(_MAX_STEPS):
        messages = [{"role": "system", "content": system}]
        if short_memory:
            messages.append({"role": "system", "content": f"Recent conversation:\n{short_memory}"})
        for role, content in turn_log:
            messages.append({"role": role, "content": content})
        messages.append({"role": "user", "content": f"QUESTION:\n{question}"})

        llm = get_llm()
        reply = llm.invoke(messages).content

        m = _FinalRe.search(reply)
        if m and m.group(1).strip():
            return m.group(1).strip()

        act = _ActionRe.search(reply)
        if act:
            action, raw_args = act.group(1).strip(), act.group(2)
            args: dict = {}
            try:
                args = json.loads(raw_args) if raw_args.strip() else {}
            except json.JSONDecodeError:
                args = {}
            result = _dispatch(action, args, question, user_id)
            turn_log.append(("assistant", reply))
            turn_log.append(("user", f"Observation:\n{result}"))
            continue

        # No recognizable structure: treat the reply as the answer.
        return reply.strip()

    return "I could not find a grounded answer in the available documents."


def _dispatch(action: str, args: dict, question: str, user_id: str) -> str:
    if action == "buscar_memoria":
        return buscar_memoria(
            query=args.get("query") or question,
            user_id=args.get("user_id") or user_id,
        )
    if action == "buscar_poliza":
        return buscar_poliza(query=args.get("query") or question, source=args.get("source"))
    return f"unknown tool {action}"


def ask(
    question: str,
    retriever,
    short_memory,
    user_id: str = "default",
    evaluate_answer: bool = False,
) -> tuple[str, float]:
    """Run one full turn through the ReAct agent (server entry point)."""
    from src import evaluate

    clean_q = check_input(question)

    answer = run_reasoning(clean_q, short_memory.to_text(), user_id=user_id)

    short_memory.add(clean_q, answer)
    remember(user_id, clean_q, answer)

    score = 0.0
    if evaluate_answer:
        contexts = [d.page_content for d in recall(user_id, clean_q)]
        score = evaluate.answer(question=clean_q, answer=answer, contexts=contexts)
    return answer, score