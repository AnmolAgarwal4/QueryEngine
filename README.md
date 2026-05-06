# Lurox

A high-performance search engine built from scratch in C — no libraries, no shortcuts.

## The Idea 
A search engine specifically designed for engineers to lookup a related topic without havnig to go through 100+ websites (Regular Updates to this will be made)


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

## Tech Stack

| Layer | Technology |
|-------|------------|
| Core Engine | C (GCC 15.2) |
| Backend API | Python |
| Database | SQLite3 |
| Data Processing | CSV + Python Scripts |
| Frontend | HTML, CSS, JavaScript |
| Search Architecture | Inverted Index |
| Hashing Algorithm | djb2 Hashing |
| Memory Management | Manual Heap Allocation (C) |
| API Integration | Python ctypes wrapper |
| Version Control | Git + GitHub |
| Deployment | Render |
| IDE | VS Code |
| Operating System | Windows |

## Structure 
Lurox/
│
├── .gitignore
├── README.md
├── render.yaml
│
├── api/
│   ├── __pycache__/
│   ├── .gitignore
│   ├── main.py
│   └── wrapper.py
│
├── Core/
│   ├── ann_engine.exe
│   ├── ann.c
│   ├── index.c
│   └── lurox_core.dll
│
├── data/
│   ├── __pycache__/
│   ├── Answers.csv
│   ├── Questions.csv
│   ├── Tags.csv
│   ├── db.py
│   ├── load_data.py
│   └── lurox.db
│
├── frontend/
│   ├── index.html
│   ├── script.js
│   └── style.css
│
└── requirements/
    └── requirements.txt



