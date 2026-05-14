import os
import time
from groq import Groq
from dotenv import load_dotenv
from hybrid import hybrid_search

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

_client = None

def get_client():
    global _client
    if _client is None:
        _client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    return _client

def rag_answer(idx, query, top_k=5, alpha=0.3):
    start = time.time()

    docs, _ = hybrid_search(idx, query, alpha=alpha, top_k=top_k)

    if not docs:
        return {
            "answer": "No relevant documents found in the index.",
            "sources": [],
            "latency_ms": round((time.time() - start) * 1000, 2)
        }

    from db import get_titles
    doc_ids = [d["doc_id"] for d in docs]
    titles = get_titles(doc_ids)

    context_parts = []
    sources = []
    for d in docs:
        title = titles.get(d["doc_id"], "Unknown")
        context_parts.append(f"- {title}")
        sources.append({
            "doc_id": d["doc_id"],
            "title": title,
            "url": f"https://stackoverflow.com/questions/{d['doc_id']}",
            "score": round(d["score"], 4)
        })

    context = "\n".join(context_parts)

    prompt = f"""You are a programming assistant. Answer the user's question based ONLY on the retrieved Stack Overflow question titles below. If the context does not contain enough information, say so honestly. Do not invent information.

Retrieved context:
{context}

User question: {query}

Provide a concise, helpful answer in 3-5 sentences, referencing which questions seem most relevant."""

    client = get_client()
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=400,
        temperature=0.3
    )

    answer = response.choices[0].message.content.strip()
    latency = (time.time() - start) * 1000

    return {
        "answer": answer,
        "sources": sources,
        "latency_ms": round(latency, 2)
    }