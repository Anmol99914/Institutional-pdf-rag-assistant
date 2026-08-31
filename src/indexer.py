# "Take all the PDFs in my uploads folder and 
# build the FAISS index."

import os
from src.pdf_processor import extract_text_from_pdf
from src.chunker import chunk_text
from src.embeddings import embed_chunks
from src.vector_store import VectorStore

def build_index_from_uploads(upload_dir, index_path, metadata_path):
    """
    Rebuilds the FAISS index from scratch using every PDF currently in upload_dir.
    Returns (store, num_files, num_chunks) or (None, 0, 0) if no usable PDFs found.
    """
    all_chunks = []
    num_files = 0

    for filename in os.listdir(upload_dir):
        if not filename.lower().endswith(".pdf"):
            continue
        pdf_path = os.path.join(upload_dir, filename)
        pages_data = extract_text_from_pdf(pdf_path)
        if not pages_data:
            continue
        chunks = chunk_text(pages_data)
        all_chunks.extend(chunks)
        num_files += 1

    if not all_chunks:
        return None, 0, 0

    embeddings = embed_chunks(all_chunks)
    store = VectorStore(dim=embeddings.shape[1])
    store.add(embeddings, all_chunks)
    store.save(index_path, metadata_path)

    return store, num_files, len(all_chunks)


def load_existing_index(index_path, metadata_path):
    """Loads a previously saved index from disk. Returns None if not found or unreadable."""
    if not (os.path.exists(index_path) and os.path.exists(metadata_path)):
        return None
    try:
        store = VectorStore(dim=384)  # dim gets overwritten by the loaded index anyway
        store.load(index_path, metadata_path)
        return store
    except Exception as e:
        print(f"Warning: failed to load existing index ({e}). Starting fresh.")
        return None