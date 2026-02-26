"""BaseFaissIPRetriever — shim for tevatron.faiss_retriever.retriever"""

import faiss
import numpy as np


class BaseFaissIPRetriever:
    """Inner-product FAISS retriever (flat index)."""

    def __init__(self, init_reps: np.ndarray):
        dim = init_reps.shape[1]
        self.index = faiss.IndexFlatIP(dim)

    def add(self, p_reps: np.ndarray) -> None:
        self.index.add(p_reps)

    def search(self, q_reps: np.ndarray, k: int):
        return self.index.search(q_reps, k)
