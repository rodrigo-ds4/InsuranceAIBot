"""Index policies into the Chroma vector store.

Run as a separate, one-off process *before* starting the server:

    python src/ingest.py

It reads every PDF under POLICIES_DIR, splits it into chunks and upserts
them into the policies collection. Re-running refreshes/rebuilds the index.

Chunking strategy
-----------------
These are legal documents organised as "Artículo" sections. Splitting purely on
character counts can cut a clause mid-sentence and hurt faithfulness. We use a
RecursiveCharacterTextSplitter that *prefers* article boundaries as separators:
articles longer than CHUNK_SIZE are split internally, while a run of short
articles is merged into one chunk (up to CHUNK_SIZE) so each chunk forms a
coherent unit with enough context.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import CHUNK_OVERLAP, CHUNK_SIZE, POLICIES_DIR, TOP_K
from src.vectorstore import get_policy_store

# Preferred separators: article headers first, then natural break points.
_SEPARATORS = [
    "\nARTÍCULO",
    "\nARTICULO",
    "\nArtículo",
    "\nARTIGO",  # not present in these docs; harmless safe-guard
    "\n\n",
    "\n",
    ". ",
    " ",
    "",
]


def make_splitter() -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=_SEPARATORS,
    )


def load_policy_docs(policies_dir: str) -> list[Document]:
    """Load each PDF into a single Document (page text concatenated) tagged by source."""
    docs = []
    for filename in sorted(os.listdir(policies_dir)):
        if not filename.lower().endswith(".pdf"):
            continue
        path = os.path.join(policies_dir, filename)
        pages = PyPDFLoader(path).load()
        if not pages:
            continue
        full_text = "\n".join(p.page_content for p in pages)
        full_text = re.sub(r"\f", "\n", full_text)  # remove form-feed page breaks
        docs.append(Document(page_content=full_text, metadata={"source": filename}))
        print(f"  loaded {filename} ({len(full_text)} chars)")
    return docs


def main() -> None:
    docs = load_policy_docs(POLICIES_DIR)
    if not docs:
        print(f"No PDFs found in {POLICIES_DIR}")
        return

    splitter = make_splitter()
    chunks: list[Document] = []
    for doc in docs:
        for piece in splitter.split_text(doc.page_content):
            chunks.append(Document(page_content=piece, metadata={"source": doc.metadata["source"]}))

    store = get_policy_store()
    reset = getattr(store, "reset_collection", None) or getattr(store, "delete_collection", None)
    if reset:
        reset()
    get_policy_store.cache_clear()
    store = get_policy_store()
    ids = store.add_documents(chunks)
    print(f"Indexed {len(ids)} chunks across {len(docs)} policy documents (top_k={TOP_K}).")


if __name__ == "__main__":
    main()