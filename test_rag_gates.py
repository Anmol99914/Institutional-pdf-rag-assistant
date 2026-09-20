
"""
Offline test of the retrieval / confidence gates in src/rag.py.

    python test_rag_gates.py

Uses the real VectorStore with hand-built vectors so each chunk has a
known similarity score. Uses a fake LLM, so no embedding model or Gemini
API call is made.

These tests are designed to match the current behavior of src/rag.py
without requiring production-code changes just for testing.
"""

import sys

import numpy as np

from src import rag
from src.vector_store import VectorStore


DIM = 32
failures = 0


def check(label, condition):
    global failures

    if condition:
        print("PASS  " + label)
    else:
        print("FAIL  " + label)
        failures += 1


def unit(i):
    """Create a one-hot vector."""
    v = np.zeros(DIM, dtype="float32")
    v[i] = 1.0
    return v


def make_store(specs):
    """
    specs:
        (source, page, text, cosine_similarity_to_query)
    """
    store = VectorStore(dim=DIM)

    for k, (src, page, text, cos) in enumerate(specs, start=1):
        v = (
            cos * unit(0)
            + np.sqrt(max(0.0, 1 - cos ** 2)) * unit(k)
        )

        store.add(
            v.reshape(1, -1),
            [{
                "source": src,
                "page": page,
                "text": text
            }]
        )

    return store


def ask(question, specs, llm_reply):
    """
    Run answer_question() using a fake LLM.

    Returns:
        result, calls
    """

    calls = []

    def fake_llm(prompt):
        calls.append(prompt)
        return llm_reply

    result = rag.answer_question(
        question,
        make_store(specs),
        lambda q: unit(0),
        fake_llm,
        top_k=3
    )

    return result, calls


def pages(result):
    """Return (source, page) pairs from displayed sources."""
    return [
        (s["source"], s["page"])
        for s in result["sources"]
    ]


# -------------------------------------------------------------------
# Test data
# -------------------------------------------------------------------

DS15 = (
    "DS.pdf",
    15,
    "Distributed systems run programs on many machines. "
    "Services offered by a server are accessed remotely."
)

DS26 = (
    "DS.pdf",
    26,
    "Remote procedure call lets programs invoke procedures on "
    "other hosts. The middleware layer hides distribution."
)

CV1 = (
    "Anmols_CV.pdf",
    1,
    "Anmol Jogi. BCA (Bachelor of Computer Applications) student "
    "at Orchid International College, Tribhuvan University."
)

Q_UNANSWERABLE = "What programs are offered by the institution?"


# ===================================================================
# 1. Nothing relevant at all
# ===================================================================

print("\n--- Nothing relevant at all: no LLM call ---")

specs = [
    DS15[:3] + (0.20,),
    DS26[:3] + (0.15,),
    CV1[:3] + (0.10,)
]

r, calls = ask(
    "Explain quantum tunnelling in semiconductors",
    specs,
    "Should never be used."
)

check(
    "no chunk qualifies -> Gemini is not called",
    len(calls) == 0
)

check(
    "result is low_confidence with no sources",
    r["low_confidence"] is True
    and r["sources"] == []
)
 
# ===================================================================
# 2. Low semantic score can be rescued by lexical relevance
# ===================================================================

print("\n--- Low semantic score with lexical rescue ---")

specs = [
    DS15[:3] + (0.24,),
    DS26[:3] + (0.21,),
    CV1[:3] + (0.18,)
]

r, calls = ask(
    "What is Remote Procedure Call?",
    specs,
    "RPC lets a program call a procedure on another host."
)

check(
    "low semantic score can be rescued by lexical relevance",
    r["low_confidence"] is False
    and len(calls) == 1
)

check(
    "rescued result contains the relevant document",
    ("DS.pdf", 26) in pages(r)
)


# ===================================================================
# 3. Confident semantic retrieval reaches the LLM
# ===================================================================

print("\n--- Confident semantic retrieval reaches the LLM ---")

specs = [
    DS26[:3] + (0.55,),
    DS15[:3] + (0.40,),
    CV1[:3] + (0.05,)
]

r, calls = ask(
    "What is Remote Procedure Call?",
    specs,
    "RPC lets a program call a procedure on another host."
)

check(
    "confident top result -> Gemini is called",
    len(calls) == 1
)

check(
    "LLM answer is returned as-is",
    r["low_confidence"] is False
    and r["answer"].startswith("RPC lets")
)

check(
    "sources are returned in semantic score order",
    pages(r) == [
        ("DS.pdf", 26),
        ("DS.pdf", 15)
    ]
)

check(
    "displayed sources match retrieved chunks 1:1",
    [
        c["page"]
        for c, _
        in r["retrieved"]
    ]
    ==
    [
        s["page"]
        for s in r["sources"]
    ]
)


# ===================================================================
# 4. Lexical rescue for phone numbers
# ===================================================================

print("\n--- Lexical rescue: phone number ---")

CV_PHONE = (
    "Anmols_CV.pdf",
    1,
    "Anmol Jogi. Phone: 9818118344. "
    "Email: anmol@example.com. Kathmandu, Nepal."
)

specs = [
    DS15[:3] + (0.18,),
    CV_PHONE[:3] + (0.16,),
    DS26[:3] + (0.12,)
]

r, calls = ask(
    "What is Anmol's phone number?",
    specs,
    "9818118344"
)

check(
    "phone question is rescued despite low embedding score",
    r["low_confidence"] is False
    and ("Anmols_CV.pdf", 1) in pages(r)
)

check(
    "Gemini is called after lexical rescue",
    len(calls) == 1
)


# ===================================================================
# 5. Lexical rescue for named person
# ===================================================================

print("\n--- Lexical rescue: named person ---")

CV_LIVE = (
    "Anmols_CV.pdf",
    1,
    "Anmol Jogi lives in Mandikhatar, Kathmandu."
)

specs = [
    DS15[:3] + (0.18,),
    CV_LIVE[:3] + (0.14,),
    DS26[:3] + (0.12,)
]

r, calls = ask(
    "Where does Anmol live?",
    specs,
    "Anmol lives in Kathmandu."
)

check(
    "named person is rescued despite low embedding score",
    r["low_confidence"] is False
    and ("Anmols_CV.pdf", 1) in pages(r)
)

check(
    "Gemini is called after name-based lexical rescue",
    len(calls) == 1
)


# ===================================================================
# 6. Phone/email structured matching
# ===================================================================

print("\n--- Structured lexical matching ---")

check(
    "phone number gets perfect lexical relevance",
    rag._lexical_relevance(
        "What is Anmol's phone number?",
        CV_PHONE[2]
    ) == 1.0
)

check(
    "email gets perfect lexical relevance",
    rag._lexical_relevance(
        "What is Anmol's email?",
        CV_PHONE[2]
    ) == 1.0
)


# ===================================================================
# 7. Entity/name matching
# ===================================================================

print("\n--- Entity/name matching ---")

check(
    "proper noun matching works",
    rag._lexical_relevance(
        "Where does Anmol live?",
        "Anmol Jogi studies BCA."
    ) == 1.0
)

check(
    "sentence-initial capital is not treated as a name",
    rag._lexical_relevance(
        "Programs offered here?",
        "Nothing relevant xyz"
    ) < 0.5
)


# ===================================================================
# 8. Source filtering for an answerable question
# ===================================================================

print("\n--- Source relevance filtering ---")

specs = [
    DS26[:3] + (0.55,),
    DS15[:3] + (0.40,),
    CV1[:3] + (0.05,)
]

r, calls = ask(
    "What is Remote Procedure Call?",
    specs,
    "RPC lets a program call a procedure on another host."
)

check(
    "irrelevant CV chunk is excluded from displayed sources",
    ("Anmols_CV.pdf", 1) not in pages(r)
)

check(
    "relevant DS chunks are preserved",
    ("DS.pdf", 26) in pages(r)
    and ("DS.pdf", 15) in pages(r)
)


# ===================================================================
# Final result
# ===================================================================

print()

if failures == 0:
    print("ALL CHECKS PASSED")
else:
    print(f"{failures} CHECK(S) FAILED")

sys.exit(1 if failures else 0)

