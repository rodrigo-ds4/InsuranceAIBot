"""Batch evaluation of the RAG pipeline over a test dataset.

Runs the full ask() flow for every row in tests/test_dataset.csv and scores
each answer with RAGAS faithfulness. Prints a per-question table plus an
average. Use it to detect regressions when you change retrieval/prompt code.

Usage:
    python src/eval_batch.py                 # uses tests/test_dataset.csv
    python src/eval_batch.py --csv path.csv  --out report.json
"""
import argparse
import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import evaluate
from src.memory.shortterm import ShortTermMemory
from src.vectorstore import get_policy_retriever


def load_dataset(path: str) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", default="tests/test_dataset.csv")
    parser.add_argument("--out", default=None, help="JSON report path")
    args = parser.parse_args()

    rows = load_dataset(args.csv)
    results = []
    short_memory = ShortTermMemory(window=0)  # isolated per question

    for i, row in enumerate(rows, 1):
        question = row["question"]
        source = row.get("source", "") or None
        reference = row.get("reference", "")

        print(f"\n[{i}/{len(rows)}] {question}")
        print(f"    policy: {source or 'all'}")

        # isolated run: fresh memory + retriever filtered to the row's policy
        retriever = get_policy_retriever(source=source or None)
        docs = retriever.invoke(question)
        contexts = [d.page_content for d in docs]

        # NOTE: reuse chain.ask() for a faithful run; here we keep it explicit:
        from src.chain import ask  # local import keeps eval hermetic

        answer, _ = ask(
            question=question,
            retriever=retriever,
            short_memory=short_memory,
            user_id=f"eval_{i}",
            evaluate_answer=False,
        )

        score = evaluate.answer(question=question, answer=answer, contexts=contexts)

        print(f"    answer: {answer[:140]!r}")
        print(f"    faithfulness: {score:.3f}")

        results.append(
            {
                "question": question,
                "source": source,
                "reference": reference,
                "answer": answer,
                "faithfulness": round(score, 4),
            }
        )

    avg = sum(r["faithfulness"] for r in results) / max(1, len(results))
    print(f"\n===== AVERAGE FAITHFULNESS: {avg:.3f} over {len(results)} questions =====")

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump({"average": round(avg, 4), "results": results}, f, ensure_ascii=False, indent=2)
        print(f"Report written to {args.out}")


if __name__ == "__main__":
    main()