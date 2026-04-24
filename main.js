const API_BASE = "http://161.153.206.126:5000";

document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    updateSystemStatus();
    
    // Autoplay forzado
    const v = document.getElementById('bg-video');
    if (v) v.play().catch(() => console.log("User interaction needed for video"));
});

async function updateSystemStatus() {
    const badge = document.getElementById('system-status-badge');
    try {
        const res = await fetch(`${API_BASE}/status`);
        const data = await res.json();
        if (data.status === "online") {
            badge.textContent = "ONLINE";
            badge.style.color = "#00ff7f";
        }
    } catch (e) {
        badge.textContent = "OFFLINE";
        badge.style.color = "#ff3232";
    }
}

async function loadProductionHistory() {
    const container = document.getElementById('renders-container');
    try {
        const res = await fetch(`${API_BASE}/history`);
        const history = await res.json();
        container.innerHTML = history.length ? history.map(item => `
            <div class="item-card">
                <span class="tiny-label">${item.timestamp}</span>
                <p style="font-weight:700; font-size:0.8rem;">${item.theme}</p>
                <p style="font-size:0.6rem; opacity:0.5; overflow:hidden;">${item.song_url}</p>
            </div>
        `).join('') : "<p style='opacity:0.3; text-align:center;'>Sin historial.</p>";
    } catch (e) { container.innerHTML = "Error cargando historial."; }
}

async function loadCatalog() {
    const container = document.getElementById('catalog-container');
    const catalog = [
        { title: "Abre mis ojos", album: "Atmos v1", theme: "Confianza" },
        { title: "Paz en la tormenta", album: "Atmos v1", theme: "Paz" },
        { title: "Victoria total", album: "Atmos v2", theme: "Victoria" }
    ];
    container.innerHTML = catalog.map(song => `
        <div class="item-card">
            <span class="tiny-label">${song.album}</span>
            <p style="font-weight:700; font-size:0.8rem;">${song.title}</p>
        </div>
    `).join('');
}

function initNavigation() {
    const navBtns = document.querySelectorAll('.nav-btn');
    const views = document.querySelectorAll('.view');

    navBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const viewId = btn.getAttribute('data-view');
            navBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            views.forEach(v => v.classList.remove('active'));
            document.getElementById(viewId).classList.add('active');
            
            if (viewId === 'catalog') loadCatalog();
            if (viewId === 'renders') loadProductionHistory();
        });
    });

    document.getElementById('btn-launch').addEventListener('click', async () => {
        const url = document.getElementById('song-url-input').value;
        const theme = document.getElementById('playlist-selector').value;
        if (!url) return alert("Ingresa un link.");
        
        const btn = document.getElementById('btn-launch');
        btn.disabled = true;
        btn.textContent = "ENVIANDO...";

        try {
            await fetch(`${API_BASE}/process`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({song_url: url, theme: theme})
            });
            alert("🚀 ¡Producción enviada!");
            document.getElementById('song-url-input').value = "";
        } catch (e) { alert("Error de conexión."); }
        finally {
            btn.disabled = false;
            btn.textContent = "INICIAR PRODUCCIÓN";
        }
    });

    document.getElementById('playlist-selector').addEventListener('change', (e) => {
        document.getElementById('current-title').textContent = e.target.value;
    });
}
