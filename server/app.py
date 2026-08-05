"""Flask + SocketIO server. Gates on config and wires the RAG chain.

Frontend protocol:
- 'message' events carry chat questions (answered via the RAG chain).
- 'action'  events carry UI actions: policy selection prefixed "POL###".
  Selecting a policy restricts subsequent retrieval to that document.
"""
import logging

from flask import Flask
from flask_socketio import SocketIO, send

from config import CORS_ALLOWED_ORIGINS, PORT, SECRET_KEY
from src.chain import ask
from src.guardrails import GuardrailsError
from src.memory.shortterm import ShortTermMemory
from src.vectorstore import get_policy_retriever

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY
socketio = SocketIO(app, cors_allowed_origins=CORS_ALLOWED_ORIGINS)

# Per-process state: short-term memory + currently selected policy.
short_memory = ShortTermMemory()
current_source = None  # e.g. "POL320130223.pdf"


def _answer(question: str) -> str:
    global current_source
    answer, _ = ask(
        question=question,
        retriever=get_policy_retriever(source=current_source),
        short_memory=short_memory,
        user_id="default",
        evaluate_answer=False,  # flip to True to score each turn
    )
    return answer


@socketio.on("action")
def handle_action(action):
    global current_source
    if not isinstance(action, str):
        send("error")
        return
    act = action.strip().upper()
    if act.startswith("POL"):
        # normalize UI code "POL320100223" -> "<code>.pdf"
        current_source = act + ".pdf"
        short_memory.clear()
        send(f"Conversemos sobre la póliza {act[3:]}. ¿Qué querés saber?")
    elif act.startswith("NEW"):
        send("Quiero generar una nueva póliza. Contame qué cobertura necesitás.")
    elif act.startswith("FND"):
        send("Te ayudo a buscar una póliza. ¿Cuál te interesa?")
    else:
        send("error")


@socketio.on("message")
def handle_message(data):
    if not isinstance(data, str) or not data.strip():
        send("Escribe una pregunta válida.")
        return
    try:
        send(_answer(data))
    except GuardrailsError as e:
        send(f"No pude procesar eso: {e}")
    except Exception:  # noqa: BLE001 - keep the chat alive
        logger.exception("chat error")
        send("Lo siento, ocurrió un error procesando tu pregunta.")


if __name__ == "__main__":
    logger.info("Starting InsuranceAIBot server on port %s", PORT)
    socketio.run(app, host="0.0.0.0", port=PORT)