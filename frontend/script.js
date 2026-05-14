const API = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8000'
    : 'https://anmol325-lurox-backend.hf.space';
let currentMode = 'bm25';

const MODE_CONFIG = {
    bm25: {
        endpoint: '/search',
        method: 'BM25',
        pipeline: 'djb2 → posting list traversal',
        complexity: 'O(1) avg · O(n) worst',
        scoreLabel: 'BM25 score',
    },
    semantic: {
        endpoint: '/semantic_search',
        method: 'Dense Semantic',
        pipeline: 'MiniLM-L6 → cosine similarity',
        complexity: 'O(n) over 384-dim vectors',
        scoreLabel: 'Cosine similarity',
    },
    hybrid: {
        endpoint: '/hybrid_search',
        method: 'Hybrid (α=0.3)',
        pipeline: 'BM25 + dense → min-max normalize → weighted sum',
        complexity: 'O(n) parallel',
        scoreLabel: 'Hybrid score',
    },
    rag: {
        endpoint: '/rag',
        method: 'RAG (Llama 3.3)',
        pipeline: 'Hybrid retrieval → top-5 context → LLM grounding',
        complexity: 'Bounded by LLM call',
        scoreLabel: 'Source relevance',
    },
};

document.querySelectorAll('.mode').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.mode').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentMode = btn.dataset.mode;
        updateStatHighlight();
    });
});

function updateStatHighlight() {
    document.querySelectorAll('.stat-val').forEach(s => s.classList.add('dim'));
    const map = { bm25: 0, semantic: 1, hybrid: 2, rag: 3 };
    const stats = document.querySelectorAll('.stat-val');
    if (stats[map[currentMode]]) {
        stats[map[currentMode]].classList.remove('dim');
    }
}

document.getElementById('query').addEventListener('keydown', e => {
    if (e.key === 'Enter') doSearch();
});

async function doSearch() {
    const term = document.getElementById('query').value.trim();
    const results = document.getElementById('results');
    const trace = document.getElementById('trace');
    const resultsHead = document.getElementById('results-head');
    const btn = document.getElementById('searchBtn');

    if (!term) return;

    const cfg = MODE_CONFIG[currentMode];

    results.innerHTML = '<p class="empty">querying ' + cfg.method + '...</p>';
    trace.style.display = 'none';
    resultsHead.style.display = 'none';
    btn.disabled = true;

    try {
        const res = await fetch(API + cfg.endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ term })
        });
        const data = await res.json();

        document.getElementById('t-method').textContent = cfg.method;
        document.getElementById('t-pipeline').textContent = cfg.pipeline;
        document.getElementById('t-latency').textContent = (data.latency_ms !== undefined ? data.latency_ms.toFixed(2) : '?') + ' ms';
        document.getElementById('t-complexity').textContent = cfg.complexity;
        trace.style.display = 'block';

        if (currentMode === 'rag') {
            renderRag(data);
        } else {
            renderResults(data, cfg.scoreLabel);
        }
    } catch (err) {
        results.innerHTML = '<p class="error">engine offline — start the API server</p>';
    } finally {
        btn.disabled = false;
    }
}

function renderResults(data, scoreLabel) {
    const results = document.getElementById('results');
    const resultsHead = document.getElementById('results-head');

    if (!data.results || data.results.length === 0) {
        results.innerHTML = '<p class="empty">no results for "' + escapeHtml(data.term) + '"</p>';
        return;
    }

    document.getElementById('results-label').textContent = 'Top ' + data.results.length + ' results';
    document.getElementById('score-label').textContent = scoreLabel;
    resultsHead.style.display = 'flex';

    results.innerHTML = data.results.map(r => `
        <div class="result" onclick="window.open('https://stackoverflow.com/questions/${r.doc_id}', '_blank')">
            <div class="result-title">${escapeHtml(r.title || 'Unknown')}</div>
            <div class="result-foot">
                <span class="result-id">doc #${r.doc_id}</span>
                <span class="result-score">${typeof r.score === 'number' ? r.score.toFixed(4) : '—'}</span>
            </div>
        </div>
    `).join('');
}

function renderRag(data) {
    const results = document.getElementById('results');
    const resultsHead = document.getElementById('results-head');

    if (!data.answer) {
        results.innerHTML = '<p class="empty">no answer generated</p>';
        return;
    }

    document.getElementById('results-label').textContent = 'Cited sources';
    document.getElementById('score-label').textContent = 'Hybrid score';
    resultsHead.style.display = 'flex';

    let html = `
        <div class="rag-answer">
            <div class="rag-label">⚡ Grounded answer</div>
            ${escapeHtml(data.answer)}
        </div>
    `;

    if (data.sources && data.sources.length > 0) {
        html += data.sources.map(s => `
            <div class="result" onclick="window.open('${s.url}', '_blank')">
                <div class="result-title">${escapeHtml(s.title)}</div>
                <div class="result-foot">
                    <span class="result-id">doc #${s.doc_id}</span>
                    <span class="result-score">${typeof s.score === 'number' ? s.score.toFixed(4) : '—'}</span>
                </div>
            </div>
        `).join('');
    }

    results.innerHTML = html;
}

function escapeHtml(s) {
    if (typeof s !== 'string') return s;
    return s.replace(/[&<>"']/g, c => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    })[c]);
}

const canvas = document.getElementById('matrix');
const ctx = canvas.getContext('2d');

canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

const particles = [];
const count = 80;

for (let i = 0; i < count; i++) {
    particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        vx: (Math.random() - 0.5) * 0.5,
        vy: (Math.random() - 0.5) * 0.5,
        radius: Math.random() * 2 + 1
    });
}

function drawParticles() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    particles.forEach(p => {
        p.x += p.vx;
        p.y += p.vy;
        if (p.x < 0 || p.x > canvas.width) p.vx *= -1;
        if (p.y < 0 || p.y > canvas.height) p.vy *= -1;

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        ctx.fillStyle = '#00ff88';
        ctx.shadowBlur = 8;
        ctx.shadowColor = '#00ff88';
        ctx.fill();
    });

    for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
            const dx = particles[i].x - particles[j].x;
            const dy = particles[i].y - particles[j].y;
            const dist = Math.sqrt(dx * dx + dy * dy);
            if (dist < 120) {
                ctx.beginPath();
                ctx.moveTo(particles[i].x, particles[i].y);
                ctx.lineTo(particles[j].x, particles[j].y);
                ctx.strokeStyle = `rgba(0, 255, 136, ${1 - dist / 120})`;
                ctx.lineWidth = 0.5;
                ctx.stroke();
            }
        }
    }

    requestAnimationFrame(drawParticles);
}

drawParticles();

window.addEventListener('resize', () => {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
});