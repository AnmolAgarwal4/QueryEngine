import csv
import requests
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'data'))
from db import init_db, save_posting, is_empty

API = "http://127.0.0.1:8000"

def load_questions(filepath, limit=5000):
    print(f"Loading {limit} questions...")
    
    init_db()
    
    with open(filepath, encoding='utf-8', errors='ignore') as f:
        reader = csv.DictReader(f)
        count = 0
        
        for row in reader:
            if count >= limit:
                break
            
            try:
                doc_id = int(row['Id'])
                title  = row['Title'].strip()
                
                if not title:
                    continue
                
                words = title.lower().split()
                for word in words:
                    word = word.strip('.,?!()')
                    if len(word) > 2:
                        requests.post(f"{API}/add", json={
                            "term": word,
                            "doc_id": doc_id
                        })
                
                count += 1
                if count % 500 == 0:
                    print(f"Loaded {count} questions...")
                    
            except Exception as e:
                continue
    
    print(f"Done. {count} questions indexed and saved to DB.")

if __name__ == "__main__":
    load_questions("data/Questions.csv", limit=5000)