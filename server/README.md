# InsuranceAIBot — server

Modern LangChain RAG backend for the insurance-policy chatbot "Nicolle".

## Stack (modern, free-tier)

| Concern        | Choice                                              |
|----------------|-----------------------------------------------------|
| Framework      | LangChain **0.3.x** (langchain-core, langchain-groq) |
| Generator LLM  | Groq `llama-3.3-70b-versatile` (free tier)           |
| Evaluator LLM  | Groq `llama-3.1-8b-instant` (cheap, for faithfulness)|
| Embeddings     | HuggingFace `all-MiniLM-L6-v2` (local, free)         |
| Vector DB      | **Chroma** (persistent, on disk)                     |
| Short-term mem | In-memory rolling window of last N turns             |
| Long-term mem  | Chroma `conversation_memory` collection              |
| Evaluation     | RAGAS `faithfulness`                                |
| Serving        | Flask + Flask-SocketIO                               |

## Layout

```
server/
├── app.py            # Flask/SocketIO entry point
├── config.py         # settings from environment (.env)
├── requirements.txt
├── .env.example      # copy to .env and fill GROQ_API_KEY
├── data/
│   ├── policies/     # put the policy PDFs here
│   └── chroma/       # vector DB (generated, gitignored)
└── src/
    ├── ingest.py     # ONE-OFF: index PDFs into Chroma (separate process)
    ├── llm.py        # Groq LLM factory (generator + evaluator)
    ├── embeddings.py # HuggingFace local embeddings (cached)
    ├── vectorstore.py# policy + memory Chroma stores & retriever
    ├── guardrails.py # input limits + prompt-injection detection
    ├── prompt.py     # persona + injection-resilient system prompt
    ├── chain.py      # RAG orchestration (retrieve → prompt → answer → memory)
    ├── evaluate.py   # RAGAS faithfulness scoring (best-effort)
    └── memory/
        ├── shortterm.py  # rolling window of last N turns (per-instant)
        └── longterm.py   # persistent conversation facts in Chroma
```

## Setup

```bash
cd server
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 1. put your policy PDFs in data/policies/
# 2. configure
cp .env.example .env   # edit GROQ_API_KEY
python src/ingest.py   # build the vector index once (separate from serving)

# 3. serve
python app.py
```

The client connects via WebSocket on port 5000.

## RAG flow (per question)

1. **Guardrails** (`guardrails.check_input`): length limit + static detection of
   common prompt-injection patterns; raises `GuardrailsError` on non-compliant input.
2. **Retrieve**: `src/vectorstore.get_policy_retriever()` → `similarity_search(k=TOP_K)`
   over the policies index.
3. **Memory**:
   - short-term: last N turns from the in-memory window;
   - long-term: `recall()` fetch relevant past exchanges from
     `conversation_memory` filtered by the user id.
4. **Prompt** (`build_messages`): system persona + boundaries; the documents and
   memory blocks are *explicitly declared untrusted data* that must not be obeyed
   as instructions (prompt-injection defense).
5. **Generate**: Groq `llama-3.3-70b-versatile`.
6. **Persist**: the exchange is written to both short and long-term memory.
7. **Evaluate (optional)**: `evaluate.answer()` scores faithfulness with **RAGAS**
   using the cheaper evaluator model.

## Evaluations

Run RAGAS faithfulness directly (requires a `.env` with an API key for the evaluator):

```bash
python - <<'EOF'
from src.evaluate import answer
score = answer(question="¿Qué cubre la hospitalización?",
               answer="La póliza reembolsa gastos de hospitalización...",
               contexts=["...chunk that supports this..."])
print("faithfulness:", score)
EOF
```

RAGAS is imported **lazily** inside `evaluate.answer()`, so the chat still works
even if evaluation is unavailable (fails to 0.0 with a warning).

## Notes

- Indexing (Chroma) is deliberately a separate process (`src/ingest.py`) from serving.
- Long-term memory and policies use **two independent Chroma collections** in the
  same on-disk store.
- Set `evaluate_answer=True` in `chain.ask()` to enable per-turn faithfulness scoring.
- Chroma and embeddings are fully local; only the Groq LLM calls an external API.