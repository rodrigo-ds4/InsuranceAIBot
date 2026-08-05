"""Central configuration. Read from environment (see .env.example)."""
import os

from dotenv import load_dotenv

load_dotenv()

# --- LLM (Groq, free tier) ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
EVAL_MODEL = os.getenv("EVAL_MODEL", "llama-3.1-8b-instant")

# --- Embeddings (HuggingFace, local & free) ---
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# --- Vector DB (Chroma) ---
DATA_DIR = os.getenv("DATA_DIR", os.path.join(os.path.dirname(__file__), "data"))
POLICIES_DIR = os.getenv("POLICIES_DIR", os.path.join(DATA_DIR, "policies"))
CHROMA_DIR = os.getenv("CHROMA_DIR", os.path.join(DATA_DIR, "chroma"))
POLICIES_COLLECTION = os.getenv("POLICIES_COLLECTION", "insurance_policies")
MEMORY_COLLECTION = os.getenv("MEMORY_COLLECTION", "conversation_memory")

# --- Retrieval tuning ---
TOP_K = int(os.getenv("TOP_K", "4"))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "120"))

# --- Guardrails ---
MAX_INPUT_CHARS = int(os.getenv("MAX_INPUT_CHARS", "500"))
MEMORY_SHORT_WINDOW = int(os.getenv("MEMORY_SHORT_WINDOW", "6"))

# --- Server ---
SECRET_KEY = os.getenv("SECRET_KEY", "dev-insecure-change-me")
CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "*").split(",")
PORT = int(os.getenv("PORT", "5000"))