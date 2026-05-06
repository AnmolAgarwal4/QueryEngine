const API = 'https://lurox.onrender.com';

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
            <div class="result-card" onclick="window.open('https://stackoverflow.com/questions/${r.doc_id}', '_blank')">
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