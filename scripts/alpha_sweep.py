import sys
import os
import time
import json
import numpy as np
import matplotlib.pyplot as plt

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'api'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'data'))

from wrapper import create_index, add, finalize
from semantic import load
from hybrid import hybrid_search
from db import init_db, load_all, get_titles

TEST_QUERIES = [
    "python error handling",
    "javascript async await",
    "sql join performance",
    "machine learning model",
    "react component lifecycle",
    "memory leak debugging",
    "snake language tutorial",
    "data structure tree",
    "api rest authentication",
    "regex pattern matching",
    "git merge conflict",
    "linux shell scripting",
]

ALPHAS = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

def build_idx():
    init_db()
    idx = create_index()
    rows = load_all()
    for term, doc_id, freq in rows:
        add(idx, term, doc_id)
    finalize(idx)
    return idx

def run_sweep(idx):
    results = {a: [] for a in ALPHAS}
    latencies = {a: [] for a in ALPHAS}

    print(f"\nRunning {len(TEST_QUERIES)} queries × {len(ALPHAS)} alphas = {len(TEST_QUERIES) * len(ALPHAS)} searches\n")

    for query in TEST_QUERIES:
        print(f"  query: {query}")
        for alpha in ALPHAS:
            start = time.time()
            docs, _ = hybrid_search(idx, query, alpha=alpha, top_k=10)
            latency = (time.time() - start) * 1000

            results[alpha].append([d["doc_id"] for d in docs])
            latencies[alpha].append(latency)

    return results, latencies

def compute_metrics(results, latencies):
    bm25_pure = results[1.0]
    semantic_pure = results[0.0]

    metrics = {}

    for alpha in ALPHAS:
        avg_overlap_bm25 = 0
        avg_overlap_sem = 0
        for i in range(len(TEST_QUERIES)):
            set_a = set(results[alpha][i])
            overlap_bm25 = len(set_a & set(bm25_pure[i])) / 10
            overlap_sem = len(set_a & set(semantic_pure[i])) / 10
            avg_overlap_bm25 += overlap_bm25
            avg_overlap_sem += overlap_sem

        avg_overlap_bm25 /= len(TEST_QUERIES)
        avg_overlap_sem /= len(TEST_QUERIES)

        diversity = 1 - (avg_overlap_bm25 + avg_overlap_sem) / 2
        avg_latency = np.mean(latencies[alpha])

        metrics[alpha] = {
            "overlap_with_bm25": round(avg_overlap_bm25, 3),
            "overlap_with_semantic": round(avg_overlap_sem, 3),
            "diversity_score": round(diversity, 3),
            "avg_latency_ms": round(avg_latency, 2),
        }

    return metrics

def plot_results(metrics):
    alphas = list(metrics.keys())
    overlap_bm25 = [metrics[a]["overlap_with_bm25"] for a in alphas]
    overlap_sem = [metrics[a]["overlap_with_semantic"] for a in alphas]
    diversity = [metrics[a]["diversity_score"] for a in alphas]
    latency = [metrics[a]["avg_latency_ms"] for a in alphas]

    fig, axes = plt.subplots(1, 2, figsize=(14, 5), facecolor='#0a0a1a')

    ax1 = axes[0]
    ax1.set_facecolor('#0a0a1a')
    ax1.plot(alphas, overlap_bm25, marker='o', color='#ff6b6b', label='Overlap with BM25', linewidth=2)
    ax1.plot(alphas, overlap_sem, marker='s', color='#00ff88', label='Overlap with Semantic', linewidth=2)
    ax1.plot(alphas, diversity, marker='^', color='#ffd93d', label='Diversity Score', linewidth=2)
    ax1.set_xlabel('Alpha (BM25 weight)', color='white')
    ax1.set_ylabel('Score', color='white')
    ax1.set_title('Hybrid Retrieval: Alpha vs Result Composition', color='#00ff88', fontweight='bold')
    ax1.legend(facecolor='#0a0a1a', edgecolor='white', labelcolor='white')
    ax1.grid(True, alpha=0.2)
    ax1.tick_params(colors='white')
    for spine in ax1.spines.values():
        spine.set_color('white')

    ax2 = axes[1]
    ax2.set_facecolor('#0a0a1a')
    ax2.plot(alphas, latency, marker='D', color='#7f77dd', linewidth=2)
    ax2.set_xlabel('Alpha (BM25 weight)', color='white')
    ax2.set_ylabel('Latency (ms)', color='white')
    ax2.set_title('Hybrid Retrieval: Latency vs Alpha', color='#00ff88', fontweight='bold')
    ax2.grid(True, alpha=0.2)
    ax2.tick_params(colors='white')
    for spine in ax2.spines.values():
        spine.set_color('white')

    plt.tight_layout()
    output = os.path.join(os.path.dirname(__file__), '..', 'benchmarks', 'alpha_sweep.png')
    plt.savefig(output, dpi=150, bbox_inches='tight', facecolor='#0a0a1a')
    print(f"\nChart saved: {output}")

def save_metrics(metrics):
    output = os.path.join(os.path.dirname(__file__), '..', 'benchmarks', 'alpha_sweep_metrics.json')
    with open(output, 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"Metrics saved: {output}")

def main():
    print("Building index...")
    idx = build_idx()

    print("Loading semantic model...")
    load()

    results, latencies = run_sweep(idx)
    metrics = compute_metrics(results, latencies)

    print("\n" + "=" * 70)
    print("ALPHA SWEEP RESULTS")
    print("=" * 70)
    print(f"{'Alpha':<8} {'BM25 Overlap':<15} {'Sem Overlap':<15} {'Diversity':<12} {'Latency':<10}")
    print("-" * 70)
    for alpha, m in metrics.items():
        print(f"{alpha:<8} {m['overlap_with_bm25']:<15} {m['overlap_with_semantic']:<15} {m['diversity_score']:<12} {m['avg_latency_ms']:<10}")

    save_metrics(metrics)
    plot_results(metrics)

    print("\nDone.")

if __name__ == "__main__":
    main()