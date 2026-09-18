import re

SIMILARITY_THRESHOLD = 0.35
LEXICAL_FALLBACK_MIN_LEXICAL = 0.50
SOURCE_RELEVANCE_RATIO = 0.55

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
    "location": {
        "live", "lives", "living", "reside", "resides", "residing",
        "located", "location", "address", "based"
    },
    "phone": {
        "phone", "number", "mobile", "contact", "telephone"
    },
    "email": {
        "email", "mail", "gmail", "e-mail"
    },
    "work": {
        "job", "work", "works", "occupation", "role", "position", "career"
    },
    "education": {
        "study", "studies", "studying", "education", "degree",
        "college", "university"
    },
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
    """Attach a lexical relevance score to each semantic candidate, keeping
    the original semantic ordering intact (vector_store.search already
    returns results sorted by semantic similarity, descending).

    Lexical/intent scoring is deliberately NOT blended into this ordering.
    It exists purely as a fallback signal for answer_question to use when
    semantic confidence fails -- letting it influence ranking universally
    previously caused well-matched semantic results (e.g. correct technical
    document chunks) to be out-ranked by unrelated chunks that happened to
    share a common word with the question.
    """
    ranked = []

    for chunk, semantic_score in results:
        lexical_score = _lexical_relevance(question, chunk["text"])
        ranked.append((chunk, semantic_score, lexical_score))

    return ranked


def _filter_relevant_results(results, top_k):
    """Keep only results that are reasonably close to the strongest match.

    This prevents weak/unrelated chunks from being displayed or sent to the
    LLM merely because top_k is fixed at 3. Multiple chunks are still kept
    when their semantic scores are reasonably close to the best result.
    """
    if not results:
        return []

    best_score = results[0][1]
    cutoff = best_score * SOURCE_RELEVANCE_RATIO

    relevant = [
        result
        for result in results
        if result[1] >= cutoff
    ]

    # Always keep the strongest result.
    if not relevant:
        relevant = [results[0]]

    return relevant[:top_k]


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


def answer_question(
    question,
    vector_store,
    embed_query_fn,
    generate_answer_fn,
    top_k=3
):
    """
    Full RAG pipeline: embed question -> retrieve candidates -> rank with
    semantic + lexical relevance -> confidence check -> filter weak sources
    -> generate answer.

    Returns dict:
    {answer, sources, retrieved, low_confidence}
    """
    query_embedding = embed_query_fn(question)
    results = vector_store.search(
        query_embedding,
        top_k=max(top_k, 10)
    )

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

    if semantically_confident:
        # Semantic ranking already found a confident match -- use it as-is.
        # No lexical reordering, so well-matched technical/domain queries
        # are never displaced by an unrelated chunk with incidental word overlap.
        selected = ranked[:top_k]

    else:
        # Semantic top-1 wasn't confident. Check every candidate for a
        # strong lexical/intent match that can rescue a paraphrased query
        # (e.g. embedding similarity is low, but the chunk clearly mentions
        # the same entity/intent as the question).
        lexical_best = max(
            ranked,
            key=lambda item: item[2]
        )

        if lexical_best[2] >= LEXICAL_FALLBACK_MIN_LEXICAL:
            rest = [
                r for r in ranked
                if r is not lexical_best
            ]

            selected = [
                lexical_best
            ] + rest[:top_k - 1]

        else:
            return {
                "answer": "I could not find sufficient information about this in the uploaded documents.",
                "sources": [],
                "retrieved": [
                    (chunk, score)
                    for chunk, score, _ in ranked
                ],
                "low_confidence": True
            }

    # Remove weak/unrelated results before sending context to the LLM
    # and before displaying them as sources.
    selected_results = [
        (chunk, score)
        for chunk, score, _ in selected
    ]

    selected_results = _filter_relevant_results(
        selected_results,
        top_k
    )

    prompt = build_prompt(
        question,
        selected_results
    )

    answer_text = generate_answer_fn(prompt)

    sources = [
        {
            "source": chunk["source"],
            "page": chunk["page"],
            "score": round(score, 4)
        }
        for chunk, score in selected_results
    ]

    return {
        "answer": answer_text,
        "sources": sources,
        "retrieved": selected_results,
        "low_confidence": False
    }