"""Index policies into the Chroma vector store.

Run as a separate, one-off process *before* starting the server:

    python src/ingest.py

It reads every PDF under POLICIES_DIR, splits it into chunks and upserts
them into the policies collection. Re-running refreshes/rebuilds the index.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import CHUNK_OVERLAP, CHUNK_SIZE, POLICIES_DIR, TOP_K
from src.vectorstore import get_policy_store


def load_policies(policies_dir: str):
    docs = []
    for filename in sorted(os.listdir(policies_dir)):
        if not filename.lower().endswith(".pdf"):
            continue
        path = os.path.join(policies_dir, filename)
        loader = PyPDFLoader(path)
        page_docs = loader.load()
        for d in page_docs:
            d.metadata["source"] = filename
        docs.extend(page_docs)
        print(f"  loaded {filename}")
    return docs


def main() -> None:
    docs = load_policies(POLICIES_DIR)
    if not docs:
        print(f"No PDFs found in {POLICIES_DIR}")
        return

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", " ", ""],
    )
    chunks = splitter.split_documents(docs)

    store = get_policy_store()
    ids = store.add_documents(chunks)
    print(f"Indexed {len(ids)} chunks across {len(docs)} pages (top_k={TOP_K}).")


if __name__ == "__main__":
    main()