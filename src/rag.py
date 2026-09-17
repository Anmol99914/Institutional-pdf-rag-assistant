import re

SIMILARITY_THRESHOLD = 0.35  # semantic-only confidence threshold
LEXICAL_FALLBACK_MIN_SIMILARITY = 0.05


def _content_words(text):
    """Return meaningful words for a lightweight lexical relevance check."""
    stopwords = {
        "a", "an", "and", "are", "as", "at", "be", "by", "can", "do", "does",
        "for", "from", "how", "i", "in", "is", "it", "me", "of", "on", "or",
        "the", "this", "to", "was", "what", "where", "which", "who", "with",
        "you", "your", "live", "lives", "located", "location", "address"
    }
    return set(re.findall(r"[a-z0-9]+", text.lower())) - stopwords


def _lexical_relevance(question, chunk_text):
    """Measure overlap between meaningful query words and a chunk."""
    query_words = _content_words(question)
    if not query_words:
        return 0.0
    chunk_words = _content_words(chunk_text)
    return len(query_words & chunk_words) / len(query_words)


def _rank_results(question, results):
    """Use semantic retrieval first, with a lexical fallback for exact factual queries.

    This helps queries such as 'Where does Anmol live?' when the embedding model
    gives a low semantic score even though the relevant chunk contains 'Anmol'.
    """
    ranked = []
    for chunk, semantic_score in results:
        lexical_score = _lexical_relevance(question, chunk["text"])
        ranked.append((chunk, semantic_score, lexical_score))

    # Keep semantic ordering unless lexical evidence is strong enough to help.
    ranked.sort(
        key=lambda item: (
            1 if item[2] > 0 else 0,
            item[2],
            item[1]
        ),
        reverse=True
    )
    return [(chunk, score) for chunk, score, _ in ranked]


def build_prompt(question, retrieved_chunks):
    """Builds a grounded RAG prompt from retrieved chunks."""
    context_blocks = []
    for chunk, score in retrieved_chunks:
        context_blocks.append(
            f"[Source: {chunk['source']}, Page {chunk['page']}]\n{chunk['text']}"
        )
    context = "\n\n---\n\n".join(context_blocks)

    prompt = f"""You are answering questions about uploaded institutional documents.
Use ONLY the retrieved context below to answer the question. Do not invent facts or use outside knowledge.
If the retrieved context does not contain enough information to answer the question, clearly state that the information was not found in the uploaded documents.

Retrieved context:
{context}

Question: {question}

Answer:"""
    return prompt


def answer_question(question, vector_store, embed_query_fn, generate_answer_fn, top_k=3):
    """
    Full RAG pipeline: embed question -> retrieve -> rank -> check confidence -> generate answer.
    Returns dict: {answer, sources, retrieved, low_confidence}
    """
    query_embedding = embed_query_fn(question)

    # Retrieve a wider candidate set so lexical evidence can rescue a weak
    # semantic match instead of being limited to the original top 3.
    results = vector_store.search(query_embedding, top_k=max(top_k, 10))
    results = _rank_results(question, results)

    if not results:
        return {
            "answer": "I could not find sufficient information about this in the uploaded documents.",
            "sources": [],
            "retrieved": results,
            "low_confidence": True
        }

    top_chunk, top_score = results[0]
    lexical_score = _lexical_relevance(question, top_chunk["text"])

    # Normal semantic confidence remains the primary path. For exact factual
    # queries, allow a strong lexical match when semantic similarity is weak.
    semantically_confident = top_score >= SIMILARITY_THRESHOLD
    lexical_fallback = (
        lexical_score > 0
        and top_score >= LEXICAL_FALLBACK_MIN_SIMILARITY
    )

    if not semantically_confident and not lexical_fallback:
        return {
            "answer": "I could not find sufficient information about this in the uploaded documents.",
            "sources": [],
            "retrieved": results,
            "low_confidence": True
        }

    # Only send the requested number of chunks to the LLM after ranking.
    selected_results = results[:top_k]
    prompt = build_prompt(question, selected_results)
    answer_text = generate_answer_fn(prompt)

    sources = [
        {"source": chunk["source"], "page": chunk["page"], "score": round(score, 4)}
        for chunk, score in selected_results
    ]

    return {
        "answer": answer_text,
        "sources": sources,
        "retrieved": selected_results,
        "low_confidence": False
    }
