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
    c.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            doc_id  INTEGER PRIMARY KEY,
            title   TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_question(doc_id, title):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT OR IGNORE INTO questions (doc_id, title)
        VALUES (?, ?)
    ''', (doc_id, title))
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

def get_titles(doc_ids):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    placeholders = ','.join('?' * len(doc_ids))
    c.execute(f'SELECT doc_id, title FROM questions WHERE doc_id IN ({placeholders})', doc_ids)
    rows = c.fetchall()
    conn.close()
    return {row[0]: row[1] for row in rows}

def is_empty():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM postings')
    count = c.fetchone()[0]
    conn.close()
    return count == 0