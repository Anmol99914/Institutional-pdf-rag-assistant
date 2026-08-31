SIMILARITY_THRESHOLD = 0.35  # below this, we treat retrieval as too weak to trust

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
    Full RAG pipeline: embed question -> retrieve -> check confidence -> generate answer.
    Returns dict: {answer, sources, retrieved, low_confidence}
    """
    query_embedding = embed_query_fn(question)
    results = vector_store.search(query_embedding, top_k=top_k)

    if not results or results[0][1] < SIMILARITY_THRESHOLD:
        return {
            "answer": "I could not find sufficient information about this in the uploaded documents.",
            "sources": [],
            "retrieved": results,
            "low_confidence": True
        }

    prompt = build_prompt(question, results)
    answer_text = generate_answer_fn(prompt)

    sources = [
        {"source": chunk["source"], "page": chunk["page"], "score": round(score, 4)}
        for chunk, score in results
    ]

    return {
        "answer": answer_text,
        "sources": sources,
        "retrieved": results,
        "low_confidence": False
    }