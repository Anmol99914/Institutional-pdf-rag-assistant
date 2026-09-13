# "Take all the PDFs in my uploads folder and 
# build the FAISS index."
import os
import time
from src.pdf_processor import extract_text_from_pdf
from src.chunker import chunk_text
from src.embeddings import embed_chunks
from src.vector_store import VectorStore
from src.md_converter import (
    pdf_pages_to_markdown,
    parse_markdown_pages,
    markdown_already_exists,
)

def _get_indexed_sources(store):
    """Returns the set of filenames already represented in the given store's metadata."""
    if store is None:
        return set()
    return set(chunk["source"] for chunk in store.metadata)


def load_existing_index(index_path, metadata_path):
    """Loads a previously saved index from disk. Returns None if not found or unreadable."""
    if not (os.path.exists(index_path) and os.path.exists(metadata_path)):
        return None
    try:
        store = VectorStore(dim=384)  # overwritten by the loaded index anyway
        store.load(index_path, metadata_path)
        return store
    except Exception as e:
        print(f"Warning: failed to load existing index ({e}). Starting fresh.")
        return None


def build_index_from_uploads(upload_dir, index_path, metadata_path):
    """
    Incrementally updates the FAISS index: only PDFs not already present in the
    existing index (identified by filename) are extracted, chunked, and embedded.
    Existing embeddings are never regenerated. Falls back to a fresh build if no
    index exists yet.

    Returns a dict: {store, total_files, total_chunks, new_files, new_chunks}
    """
    t_start = time.time()

    markdown_dir = os.path.join(upload_dir, "..", "markdown")
    markdown_dir = os.path.abspath(markdown_dir)
    os.makedirs(markdown_dir, exist_ok=True)

    existing_store = load_existing_index(index_path, metadata_path)
    already_indexed = _get_indexed_sources(existing_store)

    pdf_filenames = [f for f in os.listdir(upload_dir) if f.lower().endswith(".pdf")]
    new_filenames = [f for f in pdf_filenames if f not in already_indexed]

    def _no_new_work_result():
        total_files = len(already_indexed)
        total_chunks = len(existing_store.metadata) if existing_store else 0
        return {
            "store": existing_store,
            "total_files": total_files,
            "total_chunks": total_chunks,
            "new_files": 0,
            "new_chunks": 0,
        }

    if not new_filenames:
        return _no_new_work_result()

        # --- PDF extraction → Markdown (new files only) ---
    t_extract_start = time.time()
    markdown_paths = {}

    for filename in new_filenames:
        pdf_path = os.path.join(upload_dir, filename)

        # Step 1: Extract text from PDF using existing PyMuPDF function
        pages_data = extract_text_from_pdf(pdf_path)

        # Step 2: Save the exact extracted text as Markdown
        already_exists, md_path = markdown_already_exists(
            filename,
            markdown_dir
        )

        if not already_exists:
            md_path, md_stage_meta = pdf_pages_to_markdown(
                pages_data,
                filename,
                markdown_dir
            )
        else:
            print(f"Markdown already exists: {md_path}")

        # Store the Markdown path for the chunking stage
        markdown_paths[filename] = md_path

    t_extract_end = time.time()

        # --- Read Markdown → Chunking (new files only) ---
    t_chunk_start = time.time()
    new_chunks = []
    processed_count = 0

    for filename, md_path in markdown_paths.items():

        # IMPORTANT:
        # Read the Markdown back from disk.
        # The Markdown file is now the source of truth.

        pages_data = parse_markdown_pages(md_path, filename)
        if not pages_data:
            continue

        chunks = chunk_text(pages_data)

        new_chunks.extend(chunks)
        processed_count += 1

    t_chunk_end = time.time()

    if not new_chunks:
        return _no_new_work_result()

    # --- Embedding (new chunks only) ---
    t_embed_start = time.time()
    new_embeddings = embed_chunks(new_chunks)
    t_embed_end = time.time()

    # --- FAISS indexing (append, not rebuild) ---
    t_index_start = time.time()
    if existing_store is None:
        store = VectorStore(dim=new_embeddings.shape[1])
    else:
        store = existing_store
    store.add(new_embeddings, new_chunks)
    store.save(index_path, metadata_path)
    t_index_end = time.time()

    t_end = time.time()

    print("\n--- Indexing timing ---")
    print(f"PDF extraction: {t_extract_end - t_extract_start:.2f}s")
    print(f"Chunking: {t_chunk_end - t_chunk_start:.2f}s")
    print(f"Embedding ({len(new_chunks)} new chunks): {t_embed_end - t_embed_start:.2f}s")
    print(f"FAISS indexing: {t_index_end - t_index_start:.2f}s")
    print(f"Total processing: {t_end - t_start:.2f}s")
    print(f"New files processed: {processed_count} | Skipped (already indexed): {len(pdf_filenames) - len(new_filenames)}")
    print("-----------------------\n")

    return {
        "store": store,
        "total_files": len(_get_indexed_sources(store)),
        "total_chunks": len(store.metadata),
        "new_files": processed_count,
        "new_chunks": len(new_chunks),
    }