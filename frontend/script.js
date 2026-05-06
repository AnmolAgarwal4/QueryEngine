const API  = 'https://lurox.onrender.com';

document.getElementById('query').addEventListener('keydown', e => {
    if (e.key === 'Enter') doSearch();
});

async function doSearch() {
    const term = document.getElementById('query').value.trim();
    const box  = document.getElementById('results');

    if (!term) return;

    box.innerHTML = '<p class="empty">searching...</p>';

    try {
        const res  = await fetch(`${API}/search`, {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ term })
        });

        const data = await res.json();

        if (!data.results || data.results.length === 0) {
            box.innerHTML = `<p class="empty">no results for "${term}"</p>`;
            return;
        }

        const cards = data.results.map(r => `
            <div class="result-card">
                <div class="result-title">${r.title || 'Unknown'}</div>
                <div class="result-meta">
                    <span class="doc-id">doc #${r.doc_id}</span>
                    <span class="freq">freq: ${r.freq}</span>
                </div>
            </div>
        `).join('');

        box.innerHTML = `
            <p class="meta">${data.count} results for "${term}"</p>
            ${cards}
            <p class="latency">latency: ${data.latency_ms}ms</p>
        `;

    } catch (err) {
        box.innerHTML = `<p class="error">engine offline — start the API server</p>`;
    }
}