const API = 'http://127.0.0.1:8000';

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

    if (!data.result || data.result === 0) {
      box.innerHTML = `<p class="empty">no results for "${term}"</p>`;
      return;
    }

    box.innerHTML = `
      <p class="meta">results for "${term}"</p>
      <div class="result-card">
        <span class="doc-id">doc_id: ${data.result}</span>
        <span class="freq">found</span>
      </div>
      <p class="latency">latency: ${data.latency_ms}ms</p>
    `;

  } catch (err) {
    box.innerHTML = `<p class="error">engine offline — start the API server</p>`;
  }
}