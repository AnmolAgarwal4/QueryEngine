import time
import numpy as np
from wrapper import search as bm25_search
from semantic import load

def hybrid_search(idx, query, alpha=0.5, top_k=10):
    start = time.time()

    bm25_docs, _ = bm25_search(idx, query)
    bm25_map = {d["doc_id"]: d["score"] for d in bm25_docs}

    model, embeddings, doc_ids = load()
    query_vec = model.encode([query], normalize_embeddings=True)[0]
    semantic_scores = embeddings @ query_vec

    top_semantic_idx = np.argsort(semantic_scores)[::-1][:100]
    semantic_top = {int(doc_ids[i]): float(semantic_scores[i]) for i in top_semantic_idx}

    candidates = set(bm25_map.keys()) | set(semantic_top.keys())

    if not candidates:
        return [], round((time.time() - start) * 1000, 4)

    bm25_vals = np.array([bm25_map.get(d, 0.0) for d in candidates], dtype=np.float32)
    sem_vals  = np.array([semantic_top.get(d, 0.0) for d in candidates], dtype=np.float32)

    def norm(arr):
        mn, mx = arr.min(), arr.max()
        return np.ones_like(arr) if mx - mn < 1e-9 else (arr - mn) / (mx - mn)

    bm25_norm = norm(bm25_vals)
    sem_norm  = norm(sem_vals)

    final = alpha * bm25_norm + (1 - alpha) * sem_norm

    results = [
        {"doc_id": d, "score": float(final[i])}
        for i, d in enumerate(candidates)
    ]
    results.sort(key=lambda x: x["score"], reverse=True)
    results = results[:top_k]

    latency = (time.time() - start) * 1000
    return results, round(latency, 4)