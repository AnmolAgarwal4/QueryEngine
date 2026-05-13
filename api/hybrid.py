import time
import numpy as np
from wrapper import search as bm25_search
from semantic import load

def get_bm25_scores(idx, query):
    words = query.strip().lower().split()
    aggregate = {}
    for word in words:
        docs, _ = bm25_search(idx, word)
        for d in docs:
            aggregate[d["doc_id"]] = aggregate.get(d["doc_id"], 0.0) + d["score"]
    return aggregate

def hybrid_search(idx, query, alpha=0.5, top_k=10):
    start = time.time()

    bm25_map = get_bm25_scores(idx, query)

    model, embeddings, doc_ids = load()
    query_vec = model.encode([query], normalize_embeddings=True)[0]
    semantic_scores = embeddings @ query_vec
    semantic_map = {int(doc_ids[i]): float(semantic_scores[i]) for i in range(len(doc_ids))}

    candidates = set(bm25_map.keys()) | set(semantic_map.keys())
    if not candidates:
        return [], round((time.time() - start) * 1000, 4)

    candidates = list(candidates)
    bm25_vals = np.array([bm25_map.get(d, 0.0) for d in candidates], dtype=np.float32)
    sem_vals  = np.array([semantic_map.get(d, 0.0) for d in candidates], dtype=np.float32)

    def minmax(arr):
        mn, mx = arr.min(), arr.max()
        if mx - mn < 1e-9:
            return np.zeros_like(arr)
        return (arr - mn) / (mx - mn)

    bm25_norm = minmax(bm25_vals)
    sem_norm  = minmax(sem_vals)

    final = alpha * bm25_norm + (1 - alpha) * sem_norm

    results = [
        {"doc_id": candidates[i], "score": float(final[i])}
        for i in range(len(candidates))
    ]
    results.sort(key=lambda x: x["score"], reverse=True)
    results = results[:top_k]

    latency = (time.time() - start) * 1000
    return results, round(latency, 4)