"""Embeddings factory.

Modern LangChain entry point: HuggingFaceEmbeddings from langchain_huggingface.
Runs locally, free, no API key required. The model is cached in memory.
"""
from functools import lru_cache

from langchain_huggingface import HuggingFaceEmbeddings

from config import EMBEDDING_MODEL


@lru_cache(maxsize=1)
def get_embeddings() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
