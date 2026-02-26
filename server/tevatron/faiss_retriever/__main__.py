"""pickle_load — shim for tevatron.faiss_retriever.__main__.pickle_load"""

import pickle
import numpy as np


def pickle_load(path: str):
    """Load (reps, lookup) from a pickle file produced by tevatron encoding."""
    with open(path, "rb") as f:
        reps, lookup = pickle.load(f)
    return np.array(reps), lookup
