"""
run_evaluation.py

Runs the question set in eval_questions.py against the REAL existing
index/pipeline (load_existing_index, embed_query, generate_answer,
answer_question) -- no mocking, no new pipeline logic.

Records, per question:
- whether the expected source document appears anywhere in top_k results
  (retrieval hit)
- whether low_confidence matches expectation (answerable -> False,
  unanswerable -> True)
- response time
- the actual answer text, for manual correctness review (correctness of
  wording/content is not auto-graded -- that still needs a human read,
  per the README's "no results claimed prior to actual testing" policy)

Usage (from project root):
    python run_evaluation.py

Writes results to: data/processed/evaluation_results.csv
Prints a summary table to the console.
"""

import time
import csv
import os

from src.indexer import load_existing_index
from src.embeddings import embed_query
from src.llm import generate_answer
from src.rag import answer_question

from eval_questions import QUESTIONS

INDEX_PATH = "vector_store/faiss.index"
METADATA_PATH = "vector_store/metadata.pkl"
OUTPUT_CSV = os.path.join("data", "processed", "evaluation_results.csv")


def run():
    vector_store = load_existing_index(INDEX_PATH, METADATA_PATH)
    if vector_store is None:
        print("No existing index found -- run build_index_from_uploads() first.")
        return

    rows = []
    for i, q in enumerate(QUESTIONS, start=1):
        question = q["question"]
        expected_source = q["expected_source"]
        category = q["category"]

        t0 = time.time()
        result = answer_question(question, vector_store, embed_query, generate_answer, top_k=3)
        elapsed = time.time() - t0

        retrieved_sources = [s["source"] for s in result["sources"]]
        retrieval_hit = (expected_source in retrieved_sources) if expected_source else None

        expected_low_confidence = expected_source is None
        confidence_correct = (result["low_confidence"] == expected_low_confidence)

        row = {
            "id": i,
            "category": category,
            "question": question,
            "expected_source": expected_source or "(none - unanswerable)",
            "retrieved_sources": "; ".join(retrieved_sources) if retrieved_sources else "(none)",
            "retrieval_hit": retrieval_hit,
            "low_confidence": result["low_confidence"],
            "expected_low_confidence": expected_low_confidence,
            "confidence_correct": confidence_correct,
            "response_time_sec": round(elapsed, 2),
            "answer_text": result["answer"].replace("\n", " ")[:200],
        }
        rows.append(row)

        status = "OK" if (retrieval_hit is not False and confidence_correct) else "CHECK"
        print(f"[{status}] #{i} ({category}) {question!r} -- "
              f"hit={retrieval_hit} conf_ok={confidence_correct} time={elapsed:.2f}s")

    # --- Write CSV ---
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    # --- Summary metrics ---
    answerable_rows = [r for r in rows if r["expected_source"] != "(none - unanswerable)"]
    unanswerable_rows = [r for r in rows if r["expected_source"] == "(none - unanswerable)"]

    retrieval_hits = [r for r in answerable_rows if r["retrieval_hit"]]
    confidence_correct_all = [r for r in rows if r["confidence_correct"]]
    avg_time = sum(r["response_time_sec"] for r in rows) / len(rows)

    print("\n=== Summary ===")
    print(f"Total questions: {len(rows)}")
    print(f"Answerable questions: {len(answerable_rows)}")
    print(f"  Retrieval hit rate: {len(retrieval_hits)}/{len(answerable_rows)} "
          f"({100 * len(retrieval_hits) / len(answerable_rows):.0f}%)")
    print(f"Unanswerable questions: {len(unanswerable_rows)}")
    print(f"Confidence flag correct (all questions): {len(confidence_correct_all)}/{len(rows)} "
          f"({100 * len(confidence_correct_all) / len(rows):.0f}%)")
    print(f"Average response time: {avg_time:.2f}s")
    print(f"\nFull results written to: {OUTPUT_CSV}")
    print("Note: answer wording/content correctness is NOT auto-graded -- "
          "open the CSV and manually review 'answer_text' against the source PDFs.")


if __name__ == "__main__":
    run()
