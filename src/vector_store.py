import faiss
import numpy as np
import pickle
import os

class VectorStore:
    def __init__(self, dim):
        self.dim = dim
        self.index = faiss.IndexFlatIP(dim)  # inner product on normalized vectors = cosine similarity
        self.metadata = []  # parallel list: metadata[i] corresponds to vector i

    def add(self, embeddings, chunks):
        """embeddings: np.array (N, dim). chunks: list of N chunk dicts (metadata)."""
        normalized = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        self.index.add(normalized.astype("float32"))
        self.metadata.extend(chunks)

    def remove_by_source(self, source):
        """Removes all vectors/chunks belonging to a given source filename in-place.
        No re-embedding needed -- just drops the matching rows from the FAISS index
        and the parallel metadata list. Returns the number of chunks removed."""
        ids_to_remove = [i for i, m in enumerate(self.metadata) if m["source"] == source]
        if not ids_to_remove:
            return 0

        selector = faiss.IDSelectorBatch(np.array(ids_to_remove, dtype="int64"))
        self.index.remove_ids(selector)

        remove_set = set(ids_to_remove)
        self.metadata = [m for i, m in enumerate(self.metadata) if i not in remove_set]

        return len(ids_to_remove)

    def search(self, query_embedding, top_k=5):
        """Returns list of (chunk_metadata, similarity_score), sorted by relevance."""
        query_norm = query_embedding / np.linalg.norm(query_embedding)
        query_norm = query_norm.astype("float32").reshape(1, -1)

        scores, indices = self.index.search(query_norm, top_k)
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            results.append((self.metadata[idx], float(score)))
        return results

    def save(self, index_path, metadata_path):
        faiss.write_index(self.index, index_path)
        with open(metadata_path, "wb") as f:
            pickle.dump(self.metadata, f)

    def load(self, index_path, metadata_path):
        self.index = faiss.read_index(index_path)
        with open(metadata_path, "rb") as f:
            self.metadata = pickle.load(f)