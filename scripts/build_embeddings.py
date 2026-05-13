import sys
import os
import numpy as np
from sentence_transformers import SentenceTransformer

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'data'))
from db import get_titles, load_all

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
EMBEDDINGS_PATH = os.path.join(OUTPUT_DIR, 'embeddings.npy')
DOC_IDS_PATH = os.path.join(OUTPUT_DIR, 'doc_ids.npy')

def main():
    print("Loading documents from DB...")
    rows = load_all()
    doc_ids = sorted(set(row[1] for row in rows))
    titles_map = get_titles(doc_ids)

    documents = []
    valid_doc_ids = []
    for doc_id in doc_ids:
        title = titles_map.get(doc_id)
        if title and title != "Unknown":
            documents.append(title)
            valid_doc_ids.append(doc_id)

    print(f"Found {len(documents)} valid documents")

    print("Loading model (cached)...")
    model = SentenceTransformer('all-MiniLM-L6-v2')

    print("Generating embeddings... this takes ~30-60 sec")
    embeddings = model.encode(
        documents,
        batch_size=64,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    print(f"Embeddings shape: {embeddings.shape}")

    np.save(EMBEDDINGS_PATH, embeddings)
    np.save(DOC_IDS_PATH, np.array(valid_doc_ids))

    print(f"Saved to {EMBEDDINGS_PATH}")
    print(f"Saved to {DOC_IDS_PATH}")
    print(f"File size: ~{embeddings.nbytes / 1024 / 1024:.1f} MB")

if __name__ == "__main__":
    main()
    