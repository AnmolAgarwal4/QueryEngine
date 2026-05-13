from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from wrapper import create_index, add, search, free, finalize
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'data'))
from db import init_db, save_posting, load_all, is_empty, get_titles

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()
idx = create_index()

if not is_empty():
    print("Loading index from database...")
    rows = load_all()
    for term, doc_id, freq in rows:
        add(idx, term, doc_id)
    print(f"Loaded {len(rows)} postings from DB.")
    finalize(idx)
else:
    print("Database empty — load data using load_data.py")

class AddRequest(BaseModel):
    term: str
    doc_id: int

class SearchRequest(BaseModel):
    term: str

@app.post("/add")
def add_term(req: AddRequest):
    add(idx, req.term, req.doc_id)
    save_posting(req.term, req.doc_id)
    finalize(idx)
    return {"status": "added", "term": req.term, "doc_id": req.doc_id}

@app.post("/search")
def search_term(req: SearchRequest):
    words = req.term.strip().lower().split()

    if len(words) == 1:
        docs, ms = search(idx, words[0])
    else:
        results = []
        for word in words:
            docs, ms = search(idx, word)
            results.append({d["doc_id"]: d for d in docs})

        common_ids = set(results[0].keys())
        for r in results[1:]:
            common_ids &= set(r.keys())

        if common_ids:
            docs = [results[0][doc_id] for doc_id in common_ids]
        else:
            merged = {}
            for r in results:
                merged.update(r)
            docs = list(merged.values())

    if docs:
        docs = sorted(docs, key=lambda x: x["score"], reverse=True)
        doc_ids = [d["doc_id"] for d in docs]
        titles = get_titles(doc_ids)
        for d in docs:
            d["title"] = titles.get(d["doc_id"], "Unknown")

    return {
        "term": req.term,
        "results": docs,
        "count": len(docs),
        "latency_ms": ms
    }

@app.post("/semantic_search")
def semantic_search_endpoint(req: SearchRequest):
    from db import get_titles
    docs, ms = semantic_search(req.term, top_k=10)
    doc_ids = [d["doc_id"] for d in docs]
    titles = get_titles(doc_ids)
    for d in docs:
        d["title"] = titles.get(d["doc_id"], "Unknown")
    return {
        "term": req.term,
        "results": docs,
        "count": len(docs),
        "latency_ms": ms,
        "method": "semantic"
    }

@app.get("/health")
def health():
    return {"status": "Lurox engine running"}

from semantic import semantic_search