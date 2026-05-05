from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from wrapper import create_index, add, search, free

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

idx = create_index()

class AddRequest(BaseModel):
    term: str
    doc_id: int

class SearchRequest(BaseModel):
    term: str

@app.post("/add")
def add_term(req: AddRequest):
    add(idx, req.term, req.doc_id)
    return {"status": "added", "term": req.term, "doc_id": req.doc_id}

@app.post("/search")
def search_term(req: SearchRequest):
    result, ms = search(idx, req.term)
    return {"term": req.term, "result": result, "latency_ms": ms}

@app.get("/health")
def health():
    return {"status": "Lurox engine running"}