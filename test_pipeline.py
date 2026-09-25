from src.pdf_processor import extract_text_from_pdf
from src.chunker import chunk_text
from src.embeddings import embed_chunks, embed_query
from src.vector_store import VectorStore
from src.llm import generate_answer
from src.rag import answer_question


# ==============================
# 1. PDF → TEXT
# ==============================

pdf_path = "data/uploads_backup/Unit_1.pdf"

pages_data = extract_text_from_pdf(pdf_path)
print(f"Extracted {len(pages_data)} pages with text.")


# ==============================
# 2. TEXT → CHUNKS
# ==============================

chunks = chunk_text(pages_data)
print(f"Created {len(chunks)} chunks.")


# ==============================
# 3. CHUNKS → EMBEDDINGS
# ==============================

print("\nGenerating embeddings...")
embeddings = embed_chunks(chunks)
print(f"Embedding shape: {embeddings.shape}")


# ==============================
# 4. EMBEDDINGS → FAISS
# ==============================

print("\nBuilding FAISS index...")
store = VectorStore(dim=embeddings.shape[1])
store.add(embeddings, chunks)

print(f"Indexed {store.index.ntotal} vectors.")


# ==============================
# 5. BASIC RETRIEVAL TEST
# ==============================

test_question = "What is the meaning of management?"

print(f"\nTest query: {test_question}")

query_emb = embed_query(test_question)
results = store.search(query_emb, top_k=3)

for chunk, score in results:
    print(
        f"\nScore: {score:.4f} | "
        f"Source: {chunk['source']} | "
        f"Page: {chunk['page']}"
    )
    print(f"Text preview: {chunk['text'][:200]}...")


# ==============================
# 6. FULL RAG TEST
# ==============================

print("\n\n=== FULL RAG TEST ===")

test_questions = [
    "What is the meaning of management?",
    "What is the recipe for chocolate cake?"
]

for q in test_questions:

    print(f"\n--- Question: {q} ---")

    result = answer_question(
        q,
        store,
        embed_query,
        generate_answer,
        top_k=3
    )

    print(f"Low confidence: {result['low_confidence']}")
    print(f"Answer:\n{result['answer']}")
    print(f"Sources: {result['sources']}")