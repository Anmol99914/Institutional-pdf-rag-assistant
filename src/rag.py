import re

SIMILARITY_THRESHOLD = 0.35
LEXICAL_FALLBACK_MIN_LEXICAL = 0.50

# Common question words are ignored for lexical matching, but important
# entity/content words such as a person's name, place, skill, subject, etc.
# are retained so paraphrased questions can still find the right chunk.
STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "been", "being", "by", "can",
    "could", "did", "do", "does", "for", "from", "has", "have", "how", "i",
    "in", "is", "it", "its", "may", "me", "of", "on", "or", "please", "tell",
    "that", "the", "their", "this", "to", "was", "were", "what", "when", "where",
    "which", "who", "whom", "why", "will", "with", "would", "you", "your", "my",
    "give", "show", "list", "provide", "explain", "describe", "know", "about"
}

# Words that commonly express the same factual intent. They are normalized
# into stable shared concepts so different question wording gets similar
# lexical treatment without changing the actual user question sent to Gemini.
INTENT_GROUPS = {
    "location": {"live", "lives", "living", "reside", "resides", "residing", "located", "location", "address", "based"},
    "phone": {"phone", "number", "mobile", "contact", "telephone"},
    "email": {"email", "mail", "gmail", "e-mail"},
    "work": {"job", "work", "works", "occupation", "role", "position", "career"},
    "education": {"study", "studies", "studying", "education", "degree", "college", "university"},
}


def _normalize_words(text):
    words = set(re.findall(r"[a-z0-9]+", text.lower()))
    return words - STOPWORDS


def _intent_concepts(words):
    """Map synonymous intent words to stable shared concepts."""
    concepts = set(words)
    for label, group in INTENT_GROUPS.items():
        if words & group:
            concepts.add("__intent_" + label)
    return concepts


def _lexical_relevance(question, chunk_text):
    """Return a normalized lexical relevance score for a question/chunk pair."""
    query_words = _normalize_words(question)
    chunk_words = _normalize_words(chunk_text)
    if not query_words:
        return 0.0

    query_concepts = _intent_concepts(query_words)
    chunk_concepts = _intent_concepts(chunk_words)

    # Entity/content-word overlap is more useful than raw question-word
    # overlap. Intent concepts let 'where is' and 'address' reinforce each other.
    overlap = query_concepts & chunk_concepts
    return len(overlap) / max(1, len(query_concepts))


def _rank_results(question, results):
    """Rank semantic candidates using semantic + lexical relevance."""
    ranked = []
    for chunk, semantic_score in results:
        lexical_score = _lexical_relevance(question, chunk["text"])
        # Semantic similarity remains important, but a strong lexical/entity
        # match can rescue factual queries where MiniLM scores the paraphrase low.
        combined_score = (0.65 * lexical_score) + (0.35 * max(semantic_score, 0.0))
        ranked.append((chunk, semantic_score, lexical_score, combined_score))

    ranked.sort(key=lambda item: item[3], reverse=True)
    return [(chunk, semantic_score, lexical_score) for chunk, semantic_score, lexical_score, _ in ranked]


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
    Full RAG pipeline: embed question -> retrieve candidates -> rank with
    semantic + lexical relevance -> confidence check -> generate answer.
    Returns dict: {answer, sources, retrieved, low_confidence}
    """
    query_embedding = embed_query_fn(question)
    results = vector_store.search(query_embedding, top_k=max(top_k, 10))

    if not results:
        return {
            "answer": "I could not find sufficient information about this in the uploaded documents.",
            "sources": [],
            "retrieved": [],
            "low_confidence": True
        }

    ranked = _rank_results(question, results)
    top_chunk, top_semantic, top_lexical = ranked[0]

    semantically_confident = top_semantic >= SIMILARITY_THRESHOLD
    # A strong lexical/entity + intent match is sufficient to rescue a
    # paraphrased factual query even when the embedding similarity is very low.
    lexical_fallback = top_lexical >= LEXICAL_FALLBACK_MIN_LEXICAL

    if not semantically_confident and not lexical_fallback:
        return {
            "answer": "I could not find sufficient information about this in the uploaded documents.",
            "sources": [],
            "retrieved": [(chunk, score) for chunk, score, _ in ranked],
            "low_confidence": True
        }

    # Only pass the strongest candidates to Gemini.
    selected = ranked[:top_k]
    selected_results = [(chunk, score) for chunk, score, _ in selected]
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
