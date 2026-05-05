# Lurox

A high-performance search engine built from scratch in C — no libraries, no shortcuts.

## What was built today (Day 1)

### Inverted Index (Core/index.c)

**Simple terms:**
A search engine's core — like a library register that maps every word to which documents contain it. Instead of scanning all documents every time, we look up instantly.

**Technical terms:**
- Hash-based inverted index using djb2 hashing
- O(1) average-case term lookup via chaining
- Case-insensitive term normalization
- Heap-allocated index to handle large struct size
- Posting list per term storing doc_id and frequency

**Data structures used:**
- Hash table (size 512, power-of-2 for fast modulo)
- Linked chaining for collision resolution
- Struct-based posting lists

### Search Function

**Simple terms:**
Type a word — get back which documents have it and how many times, in milliseconds.

**Technical terms:**
- Hash-based O(1) lookup
- Returns posting list with doc_id and frequency
- Latency measured using clock_t in milliseconds

## Setup

    gcc Core/index.c -o Core/index_engine.exe
    Core\index_engine.exe

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Core engine | C (GCC 15.2) |
| Version control | Git + GitHub |
| IDE | VS Code |

## Roadmap

- [x] Day 1 — Inverted index (C)
- [ ] Day 2 — ANN engine / KD-Tree (C)
- [ ] Day 3 — Python wrapper (ctypes)
- [ ] Day 4 — Ranking logic
- [ ] Day 5 — FastAPI backend
- [ ] Day 6 — JS Frontend
- [ ] Day 7 — AWS Deploy