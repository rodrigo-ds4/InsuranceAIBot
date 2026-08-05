"""Vector stores backed by Chroma (persistent).

Two independent Chroma databases:
- policies: one-off embeddings of the insurance policy documents (long-term reference)
- memory:   conversational memory (facts the assistant learned about the user)

Modern LangChain entry point: langchain_chroma.Chroma with a persistent client.
Returns a Retriever for queries. Indexing is done separately (see ingest.py).
"""
from functools import lru_cache

from langchain_chroma import Chroma
from langchain_core.vectorstores import VectorStoreRetriever

from config import (
    CHROMA_DIR,
    MEMORY_COLLECTION,
    POLICIES_COLLECTION,
    TOP_K,
)
from src.embeddings import get_embeddings


def _store(collection: str) -> Chroma:
    return Chroma(
        collection_name=collection,
        persist_directory=CHROMA_DIR,
        embedding_function=get_embeddings(),
    )


@lru_cache(maxsize=1)
def get_policy_store() -> Chroma:
    """Read/write access to the insurance-policies index."""
    return _store(POLICIES_COLLECTION)


@lru_cache(maxsize=1)
def get_memory_store() -> Chroma:
    """Read/write access to the conversational-memory index."""
    return _store(MEMORY_COLLECTION)


def get_policy_retriever(source: str | None = None) -> VectorStoreRetriever:
    """Retriever used by the RAG chain. Optionally filter to one policy PDF.

    - source=None  → search across all indexed policies.
    - source="POLX.pdf" → restrict to that document.
    """
    kwargs: dict = {"k": TOP_K}
    if source:
        kwargs["filter"] = {"source": source}
    return get_policy_store().as_retriever(search_type="similarity", search_kwargs=kwargs)