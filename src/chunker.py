def chunk_text(pages_data, chunk_size=600, overlap=100):
    """
    Splits page-level text into overlapping word-based chunks.
    chunk_size and overlap are measured in words.
    Returns a list of dicts: {chunk_id, text, source, page}
    """
    chunks = []
    chunk_id = 0

    for page_entry in pages_data:
        words = page_entry["text"].split()
        start = 0
        while start < len(words):
            end = start + chunk_size
            chunk_words = words[start:end]
            chunk_text_str = " ".join(chunk_words)

            chunks.append({
                "chunk_id": chunk_id,
                "text": chunk_text_str,
                "source": page_entry["source"],
                "page": page_entry["page"]
            })
            chunk_id += 1

            if end >= len(words):
                break
            start = end - overlap  # step forward with overlap

    return chunks