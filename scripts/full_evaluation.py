import sys
import os
import time
import json
import numpy as np
import matplotlib.pyplot as plt

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'api'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'data'))

from wrapper import create_index, add, finalize, search as bm25_search
from semantic import semantic_search, load
from hybrid import hybrid_search
from rag import rag_answer
from db import init_db, load_all

TEST_QUERIES = [
    "python error handling",
    "javascript async programming",
    "sql join performance",
    "git merge conflict",
    "react component lifecycle",
    "regex pattern matching",
    "machine learning model",
    "memory leak debugging",
]

def build_idx():
    init_db()
    idx = create_index()
    rows = load_all()
    for term, doc_id, freq in rows:
        add(idx, term, doc_id)
    finalize(idx)
    return idx

def eval_bm25(idx, queries):
    latencies, results = [], []
    for q in queries:
        start = time.time()
        words = q.lower().split()
        merged = {}
        for w in words:
            docs, _ = bm25_search(idx, w)
            for d in docs:
                merged[d["doc_id"]] = merged.get(d["doc_id"], 0) + d["score"]
        sorted_docs = sorted(merged.items(), key=lambda x: x[1], reverse=True)[:10]
        latencies.append((time.time() - start) * 1000)
        results.append([d[0] for d in sorted_docs])
    return latencies, results

def eval_semantic(queries):
    latencies, results = [], []
    for q in queries:
        start = time.time()
        docs, _ = semantic_search(q, top_k=10)
        latencies.append((time.time() - start) * 1000)
        results.append([d["doc_id"] for d in docs])
    return latencies, results

def eval_hybrid(idx, queries):
    latencies, results = [], []
    for q in queries:
        start = time.time()
        docs, _ = hybrid_search(idx, q, alpha=0.3, top_k=10)
        latencies.append((time.time() - start) * 1000)
        results.append([d["doc_id"] for d in docs])
    return latencies, results

def eval_rag(idx, queries):
    latencies, answer_lengths = [], []
    for q in queries:
        start = time.time()
        result = rag_answer(idx, q, top_k=5, alpha=0.3)
        latencies.append((time.time() - start) * 1000)
        answer_lengths.append(len(result["answer"].split()))
    return latencies, answer_lengths

def plot_results(metrics):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), facecolor='#0a0a1a')

    methods = ['BM25', 'Semantic', 'Hybrid', 'RAG']
    colors = ['#ff6b6b', '#00ff88', '#ffd93d', '#7f77dd']

    ax1 = axes[0]
    ax1.set_facecolor('#0a0a1a')
    avg_latencies = [metrics[m]['avg_latency'] for m in methods]
    bars = ax1.bar(methods, avg_latencies, color=colors, edgecolor='white', linewidth=1.5)
    for bar, val in zip(bars, avg_latencies):
        ax1.text(bar.get_x() + bar.get_width()/2, val * 1.05,
                 f'{val:.1f}ms', ha='center', color='white', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Latency (ms)', color='white')
    ax1.set_title('Lurox: Latency by Method', color='#00ff88', fontweight='bold', pad=15)
    ax1.set_yscale('log')
    ax1.tick_params(colors='white')
    for spine in ax1.spines.values():
        spine.set_color('white')

    ax2 = axes[1]
    ax2.set_facecolor('#0a0a1a')
    retrieval_methods = ['BM25', 'Semantic', 'Hybrid']
    retrieval_colors = colors[:3]
    diversities = [metrics[m]['unique_results'] for m in retrieval_methods]
    bars = ax2.bar(retrieval_methods, diversities, color=retrieval_colors, edgecolor='white', linewidth=1.5)
    for bar, val in zip(bars, diversities):
        ax2.text(bar.get_x() + bar.get_width()/2, val + 0.5,
                 f'{val:.1f}', ha='center', color='white', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Unique Results per Query (avg)', color='white')
    ax2.set_title('Lurox: Result Diversity', color='#00ff88', fontweight='bold', pad=15)
    ax2.tick_params(colors='white')
    for spine in ax2.spines.values():
        spine.set_color('white')

    plt.tight_layout()
    output = os.path.join(os.path.dirname(__file__), '..', 'benchmarks', 'full_evaluation.png')
    plt.savefig(output, dpi=150, bbox_inches='tight', facecolor='#0a0a1a')
    print(f"\nChart saved: {output}")

def main():
    print("Building index...")
    idx = build_idx()
    print("Loading semantic model...")
    load()

    print(f"\nRunning evaluation on {len(TEST_QUERIES)} queries × 4 methods\n")

    print("[1/4] BM25...")
    bm25_lat, bm25_res = eval_bm25(idx, TEST_QUERIES)

    print("[2/4] Semantic...")
    sem_lat, sem_res = eval_semantic(TEST_QUERIES)

    print("[3/4] Hybrid...")
    hyb_lat, hyb_res = eval_hybrid(idx, TEST_QUERIES)

    print("[4/4] RAG (slowest, LLM calls)...")
    rag_lat, rag_lens = eval_rag(idx, TEST_QUERIES)

    all_results = bm25_res + sem_res + hyb_res
    unique_per_query = [len(set(r)) for r in all_results]

    metrics = {
        'BM25': {
            'avg_latency': round(np.mean(bm25_lat), 2),
            'p99_latency': round(np.percentile(bm25_lat, 99), 2),
            'unique_results': round(np.mean([len(set(r)) for r in bm25_res]), 2),
        },
        'Semantic': {
            'avg_latency': round(np.mean(sem_lat), 2),
            'p99_latency': round(np.percentile(sem_lat, 99), 2),
            'unique_results': round(np.mean([len(set(r)) for r in sem_res]), 2),
        },
        'Hybrid': {
            'avg_latency': round(np.mean(hyb_lat), 2),
            'p99_latency': round(np.percentile(hyb_lat, 99), 2),
            'unique_results': round(np.mean([len(set(r)) for r in hyb_res]), 2),
        },
        'RAG': {
            'avg_latency': round(np.mean(rag_lat), 2),
            'p99_latency': round(np.percentile(rag_lat, 99), 2),
            'avg_answer_words': round(np.mean(rag_lens), 1),
        },
    }

    print("\n" + "=" * 70)
    print("LUROX 2.0 — FULL EVALUATION RESULTS")
    print("=" * 70)
    for method, m in metrics.items():
        print(f"\n{method}:")
        for k, v in m.items():
            print(f"  {k}: {v}")

    output = os.path.join(os.path.dirname(__file__), '..', 'benchmarks', 'full_evaluation_metrics.json')
    with open(output, 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"\nMetrics saved: {output}")

    plot_results(metrics)
    print("\nDone.")

if __name__ == "__main__":
    main()