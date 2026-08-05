"""Short-term memory: last N chat lines.

Keeps the last MEMORY_SHORT_WINDOW user/assistant turns in memory as plain
text, injected into the prompt so the model has immediate conversational
context without persisting anything.
"""
from config import MEMORY_SHORT_WINDOW


class ShortTermMemory:
    def __init__(self, window: int = MEMORY_SHORT_WINDOW) -> None:
        self.window = window
        self.turns: list[tuple[str, str]] = []

    def add(self, user: str, assistant: str) -> None:
        self.turns.append((user, assistant))
        if len(self.turns) > self.window:
            self.turns = self.turns[-self.window:]

    def to_text(self) -> str:
        if not self.turns:
            return ""
        lines = []
        for user, assistant in self.turns[:-1]:  # exclude the current question
            lines.append(f"- Usuario: {user}\n- Asistente: {assistant}")
        return "\n".join(lines)

    def clear(self) -> None:
        self.turns = []