"""Guardrails: input sanity, persona limits and prompt-injection protection.

Layered, simple approach:
1. Length / type checks on the raw input.
2. Static detection of common injection phrases (ignore instructions, etc.).
3. Prompt construction that makes injected content a *fact*, not an
   instruction (see prompt.py). The model is told the source docs may be
   untrusted and are never to be followed as directives.
"""
import re

from config import MAX_INPUT_CHARS

# Patterns commonly used to re-write/ignore instructions.
_INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?(previous\s+)?instructions", re.I),
    re.compile(r"ignore\s+your\s+(role|prompt|system)", re.I),
    re.compile(r"disregard\s+(your\s+|the\s+)?(role|prompt|system)", re.I),
    re.compile(r"forget\s+your\s+(instructions|role|rules)", re.I),
    re.compile(r"without\s+(following|respecting)\s+(your\s+)?(instructions|rules)", re.I),
    re.compile(r"reveal\s+your\s+(system\s+)?prompt", re.I),
    re.compile(r"\bdo\s+anything\s+now\b", re.I),
    re.compile(r"\bjailbreak\b", re.I),
]


class GuardrailsError(Exception):
    pass


def sanitize(text: str) -> str:
    """Enforce length and basic type checks. Raises GuardrailsError."""
    if not isinstance(text, str):
        raise GuardrailsError("Input must be text.")
    text = text.strip()
    if not text:
        raise GuardrailsError("Empty input.")
    if len(text) > MAX_INPUT_CHARS:
        raise GuardrailsError(f"Input too long (>{MAX_INPUT_CHARS} chars).")
    return text


def looks_like_injection(text: str) -> bool:
    return any(p.search(text) for p in _INJECTION_PATTERNS)


def check_input(raw: str) -> str:
    """Full guardrail pass. Returns the clean text or raises."""
    clean = sanitize(raw)
    if looks_like_injection(clean):
        raise GuardrailsError("Blocked: suspicious prompt-injection pattern.")
    return clean