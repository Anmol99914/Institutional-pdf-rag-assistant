import os
import torch
from sentence_transformers import SentenceTransformer

_model = None


def get_model():
    """Lazy-loads the embedding model once and reuses it for the life of the process."""
    global _model
    if _model is None:
        # Match thread count to available CPU cores - on weak/old CPUs the default
        # thread configuration doesn't always use the hardware well.
        try:
            torch.set_num_threads(os.cpu_count() or 1)
        except Exception:
            pass

        _model = SentenceTransformer("all-MiniLM-L6-v2")

        # Dynamic quantization (int8) speeds up CPU inference on the model's linear
        # layers, typically 2-3x, with negligible accuracy loss. This does not change
        # the model or its weights - only how they're executed at inference time.
        # Wrapped in try/except: if quantization isn't supported in this environment,
        # we silently fall back to the unquantized model rather than breaking anything.
        try:
            transformer_module = _model._first_module()
            transformer_module.auto_model = torch.quantization.quantize_dynamic(
                transformer_module.auto_model, {torch.nn.Linear}, dtype=torch.qint8
            )
        except Exception as e:
            print(f"Note: CPU quantization not applied ({e}). Using standard model.")

    return _model


def embed_chunks(chunks, batch_size=32):
    """
    Takes a list of chunk dicts (each with a "text" field).
    Returns a numpy array of embeddings, shape (num_chunks, embedding_dim).
    """
    model = get_model()
    texts = [chunk["text"] for chunk in chunks]
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=True,
        convert_to_numpy=True
    )
    return embeddings


def embed_query(query):
    """Embeds a single question string. Returns a 1D numpy array."""
    model = get_model()
    return model.encode([query], convert_to_numpy=True)[0]