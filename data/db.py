import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'lurox.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS postings (
            term    TEXT,
            doc_id  INTEGER,
            freq    INTEGER,
            PRIMARY KEY (term, doc_id)
        )
    ''')
    conn.commit()
    conn.close()

def save_posting(term, doc_id, freq=1):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO postings (term, doc_id, freq)
        VALUES (?, ?, ?)
        ON CONFLICT(term, doc_id) DO UPDATE SET freq = freq + 1
    ''', (term.lower(), doc_id, freq))
    conn.commit()
    conn.close()

def load_all():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT term, doc_id, freq FROM postings')
    rows = c.fetchall()
    conn.close()
    return rows

def is_empty():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM postings')
    count = c.fetchone()[0]
    conn.close()
    return count == 0