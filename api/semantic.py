import os
import numpy as np
from sentence_transformers import SentenceTransformer

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
EMBEDDINGS_PATH = os.path.join(DATA_DIR, 'embeddings.npy')
DOC_IDS_PATH = os.path.join(DATA_DIR, 'doc_ids.npy')

_model = None
_embeddings = None
_doc_ids = None

def load():
    global _model, _embeddings, _doc_ids
    if _model is None:
        _model = SentenceTransformer('all-MiniLM-L6-v2')
        _embeddings = np.load(EMBEDDINGS_PATH)
        _doc_ids = np.load(DOC_IDS_PATH)
    return _model, _embeddings, _doc_ids

def semantic_search(query, top_k=10):
    import time
    model, embeddings, doc_ids = load()

    start = time.time()
    query_vec = model.encode([query], normalize_embeddings=True)[0]
    scores = embeddings @ query_vec
    top_idx = np.argsort(scores)[::-1][:top_k]
    latency = (time.time() - start) * 1000

    results = [
        {"doc_id": int(doc_ids[i]), "score": float(scores[i])}
        for i in top_idx
    ]
    return results, round(latency, 4)