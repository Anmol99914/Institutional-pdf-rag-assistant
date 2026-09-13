"""
eval_questions.py

Test question set for the evaluation phase. Mix of answerable questions
(across all 3 currently-indexed PDFs) and deliberately unanswerable ones,
plus a couple of short/acronym-style queries to document the known
retrieval-sensitivity limitation from the RPC investigation.

Fields:
- question: the query text
- expected_source: filename the answer should be grounded in, or None
  if the question is deliberately unanswerable / out of scope
- category: for grouping in the results summary
"""

QUESTIONS = [
    # --- Unit 1: Introduction to Management ---
    {"question": "What is the meaning of management?",
     "expected_source": "Unit 1 - Introduction to Management.pdf", "category": "answerable-core"},
    {"question": "What are the characteristics of management?",
     "expected_source": "Unit 1 - Introduction to Management.pdf", "category": "answerable-core"},
    {"question": "How is management related to organization?",
     "expected_source": "Unit 1 - Introduction to Management.pdf", "category": "answerable-detail"},
    {"question": "What resources does management coordinate?",
     "expected_source": "Unit 1 - Introduction to Management.pdf", "category": "answerable-detail"},

    # --- Unit 2: Perspectives in Management ---
    {"question": "What is scientific management?",
     "expected_source": "Unit 2 - Perspectives in management.pdf", "category": "answerable-core"},
    {"question": "Who was Frederick W. Taylor?",
     "expected_source": "Unit 2 - Perspectives in management.pdf", "category": "answerable-core"},
    {"question": "What are Fayol's principles of management?",
     "expected_source": "Unit 2 - Perspectives in management.pdf", "category": "answerable-detail"},
    {"question": "What did Elton Mayo discover in the Hawthorne studies?",
     "expected_source": "Unit 2 - Perspectives in management.pdf", "category": "answerable-detail"},
    {"question": "What is bureaucratic management theory?",
     "expected_source": "Unit 2 - Perspectives in management.pdf", "category": "answerable-detail"},

    # --- DS.pdf: Distributed Systems ---
    {"question": "What is the definition of a distributed system?",
     "expected_source": "DS.pdf", "category": "answerable-core"},
    {"question": "What are the design goals of a distributed system?",
     "expected_source": "DS.pdf", "category": "answerable-core"},
    {"question": "What is Remote Procedure Call in distributed systems?",
     "expected_source": "DS.pdf", "category": "answerable-detail"},
    {"question": "What is the difference between cluster computing and grid computing?",
     "expected_source": "DS.pdf", "category": "answerable-detail"},
    {"question": "What are the types of transparency in distributed systems?",
     "expected_source": "DS.pdf", "category": "answerable-detail"},

    # --- Deliberately unanswerable / out of scope ---
    {"question": "What is the boiling point of mercury?",
     "expected_source": None, "category": "unanswerable"},
    {"question": "Who won the 2022 FIFA World Cup?",
     "expected_source": None, "category": "unanswerable"},
    {"question": "What is the capital of France?",
     "expected_source": None, "category": "unanswerable"},
    {"question": "Summarize the plot of Romeo and Juliet.",
     "expected_source": None, "category": "unanswerable"},

    # --- Short/acronym-style queries (known limitation stress test) ---
    {"question": "RPC",
     "expected_source": "DS.pdf", "category": "acronym-stress"},
    {"question": "LAN vs WAN",
     "expected_source": "DS.pdf", "category": "acronym-stress"},
    {"question": "ACID properties",
     "expected_source": "DS.pdf", "category": "acronym-stress"},
]
