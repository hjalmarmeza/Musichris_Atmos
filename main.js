const API_BASE = "http://161.153.206.126:5000";

document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    fetchStats();
    loadProductionHistory();
    
    // Autoplay blindado para iOS
    const v = document.getElementById('bg-video');
    if (v) v.play().catch(() => {});
});

async function fetchStats() {
    const potentialDisplay = document.getElementById('video-potential');
    try {
        const res = await fetch(`${API_BASE}/stats`);
        const data = await res.json();
        const theme = document.getElementById('playlist-selector').value;
        const isReady = data.ready[theme] || false;
        
        if (isReady) {
            potentialDisplay.textContent = "LISTO (Playlist Variada)";
            potentialDisplay.style.color = "#00ff7f";
        } else {
            potentialDisplay.textContent = "NECESITA MÁS TEMAS";
            potentialDisplay.style.color = "#ffcc00";
        }
    } catch (e) {
        console.warn("Error stats");
    }
}

async function loadCatalog() {
    const container = document.getElementById('catalog-container');
    container.innerHTML = "<p style='text-align:center; opacity:0.5;'>Conectando con biblioteca Oracle...</p>";
    
    try {
        const res = await fetch(`${API_BASE}/catalog`);
        const catalog = await res.json();
        
        container.innerHTML = catalog.map(song => `
            <div class="item-card" style="display:flex; justify-content:space-between; align-items:center; opacity: ${song.disabled ? '0.4' : '1'}">
                <div>
                    <span class="tiny-label">${song.album}</span>
                    <p style="font-weight:700; font-size:0.8rem;">${song.title}</p>
                </div>
                <input type="checkbox" ${song.disabled ? '' : 'checked'} onchange="toggleSong('${song.filename}', !this.checked)">
            </div>
        `).join('');
    } catch (e) {
        container.innerHTML = "<p style='text-align:center; opacity:0.5;'>⚠️ Error de conexión.</p>";
    }
}

async function toggleSong(filename, disabled) {
    try {
        await fetch(`${API_BASE}/toggle_song`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ filename, disabled })
        });
        fetchStats(); // Recargar stats al cambiar canciones
    } catch (e) { alert("Error al actualizar estado."); }
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
                <div style="font-size:0.5rem; background:var(--accent-blue); padding:2px 8px; border-radius:10px; display:inline-block; margin-top:5px;">${item.status}</div>
            </div>
        `).join('') : "<p style='opacity:0.3; text-align:center;'>Sin historial.</p>";
    } catch (e) { console.error("Error historial"); }
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

    const selector = document.getElementById('playlist-selector');
    if (selector) {
        selector.addEventListener('change', () => {
            document.getElementById('current-title').textContent = "Producción: " + selector.value;
            fetchStats();
        });
    }

    document.getElementById('btn-launch').addEventListener('click', launchProduction);
}

async function launchProduction() {
    const btn = document.getElementById('btn-launch');
    const url = document.getElementById('song-url-input').value;
    const theme = document.getElementById('playlist-selector').value;
    
    if (!url) return alert("Por favor ingresa un link.");

    btn.disabled = true;
    btn.textContent = "EN COLA DE NUBE...";

    try {
        const response = await fetch(`${API_BASE}/process`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ song_url: url, theme: theme })
        });
        if (response.ok) {
            alert("🚀 ¡Misión iniciada! Revisa el Historial.");
            document.getElementById('song-url-input').value = "";
        }
    } catch (e) { alert("Error de conexión."); }
    finally {
        btn.disabled = false;
        btn.textContent = "INICIAR PRODUCCIÓN";
        loadProductionHistory();
    }
}
