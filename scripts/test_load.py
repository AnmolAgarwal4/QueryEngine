import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'data'))

from db import get_titles, load_all

rows = load_all()
print(f"Total postings in DB: {len(rows)}")

doc_ids = list(set(row[1] for row in rows))
print(f"Unique documents: {len(doc_ids)}")

sample_ids = doc_ids[:5]
titles = get_titles(sample_ids)

print("\nSample documents:")
for doc_id in sample_ids:
    print(f"  doc_id={doc_id} | title={titles.get(doc_id, 'Unknown')}")