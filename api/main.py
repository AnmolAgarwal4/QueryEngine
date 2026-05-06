from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from wrapper import create_index, add, search, free
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'data'))
from db import init_db, save_posting, load_all, is_empty

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
    return {"status": "added", "term": req.term, "doc_id": req.doc_id}

@app.post("/search")
def search_term(req: SearchRequest):
    docs, ms = search(idx, req.term)
    return {
        "term": req.term,
        "results": docs,
        "count": len(docs),
        "latency_ms": ms
    }

@app.get("/health")
def health():
    return {"status": "Lurox engine running"}