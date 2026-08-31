from sentence_transformers import SentenceTransformer

_model = None

def get_model():
    """Lazy-load the embedding model so it's only loaded once."""
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def embed_chunks(chunks):
    """
    Takes a list of chunk dicts (each with a "text" field).
    Returns a numpy array of embeddings, shape (num_chunks, embedding_dim).
    """
    model = get_model()
    texts = [chunk["text"] for chunk in chunks]
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
    return embeddings

def embed_query(query):
    """Embeds a single question string. Returns a 1D numpy array."""
    model = get_model()
    return model.encode([query], convert_to_numpy=True)[0]