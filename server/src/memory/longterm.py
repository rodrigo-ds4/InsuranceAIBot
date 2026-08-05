"""Long-term memory: persistent conversation history in Chroma.

Each user/assistant exchange is stored as an embedding in the memory
collection. Before answering, the most relevant past exchanges are retrieved
so the bot "remembers" recurring context across sessions.
"""
from langchain_core.documents import Document

from config import TOP_K
from src.vectorstore import get_memory_store


def remember(user: str, question: str, answer: str) -> None:
    get_memory_store().add_documents(
        [Document(page_content=f"Q: {question}\nA: {answer}", metadata={"user": user})]
    )


def recall(user: str, question: str) -> list[Document]:
    return get_memory_store().similarity_search(
        question,
        k=TOP_K,
        filter={"user": user},
    )