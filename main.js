const API_BASE = "http://161.153.206.126:5000";

document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    updateSystemStatus();
    loadProductionHistory();
    
    // Forzar autoplay si el navegador bloqueó
    const video = document.getElementById('bg-video');
    if (video) {
        video.muted = true;
        video.play().catch(e => console.log("Autoplay waiting for interaction"));
    }
});

async function updateSystemStatus() {
    const badge = document.getElementById('system-status-badge');
    try {
        const res = await fetch(`${API_BASE}/status`);
        const data = await res.json();
        if (data.status === "online") {
            badge.textContent = "CONECTADO";
            badge.style.color = "#00ff7f";
        }
    } catch (e) {
        badge.textContent = "DESCONECTADO";
        badge.style.color = "#ff3232";
    }
}

async function loadProductionHistory() {
    const container = document.getElementById('renders-container');
    if (!container) return;

    try {
        const res = await fetch(`${API_BASE}/history`);
        const history = await res.json();
        
        if (history.length === 0) {
            container.innerHTML = "<p style='opacity:0.5; text-align:center;'>No hay envíos recientes.</p>";
            return;
        }

        container.innerHTML = history.map(item => `
            <div class="stat-card">
                <span class="label">${item.timestamp}</span>
                <span class="value" style="font-size:0.8rem; display:block;">${item.theme}</span>
                <div class="status-badge" style="background:var(--accent-color); margin-top:5px;">${item.status}</div>
            </div>
        `).join('');
    } catch (e) {
        console.error("Error historial");
    }
}

async function loadCatalog() {
    const container = document.getElementById('catalog-container');
    if (!container) return;
    
    // Mock de catálogo ministerial
    const catalog = [
        { title: "Abre mis ojos", album: "Atmos v1", theme: "Confianza" },
        { title: "Paz en la tormenta", album: "Atmos v1", theme: "Paz" },
        { title: "Victoria total", album: "Atmos v2", theme: "Victoria" }
    ];

    container.innerHTML = catalog.map(song => `
        <div class="stat-card">
            <span class="label">${song.album}</span>
            <span class="value" style="font-size:0.8rem">${song.title}</span>
            <div style="font-size:0.6rem; opacity:0.5">${song.theme}</div>
        </div>
    `).join('');
}

async function launchProduction() {
    const btn = document.getElementById('btn-launch');
    const songUrlInput = document.getElementById('song-url-input');
    const themeSelector = document.getElementById('playlist-selector');
    
    const song_url = songUrlInput ? songUrlInput.value : "";
    const theme = themeSelector.value;

    if (!song_url) {
        alert("Por favor ingresa un link ministerial.");
        return;
    }

    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> PROCESANDO...';

    try {
        const response = await fetch(`${API_BASE}/process`, { 
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ song_url, theme })
        });
        
        if (response.ok) {
            alert("🚀 ¡Misión iniciada en la nube!");
            if (songUrlInput) songUrlInput.value = "";
        }
    } catch (err) {
        alert("⚠️ Error de conexión.");
    } finally {
        btn.disabled = false;
        btn.innerHTML = 'INICIAR PRODUCCIÓN EN NUBE';
        loadProductionHistory();
    }
}

function initNavigation() {
    const navButtons = document.querySelectorAll('.btn-nav');
    const views = document.querySelectorAll('.view');

    navButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const viewId = btn.getAttribute('data-view');
            navButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            views.forEach(v => v.classList.remove('active'));
            document.getElementById(viewId).classList.add('active');
            
            if (viewId === 'catalog') loadCatalog();
            if (viewId === 'renders') loadProductionHistory();
        });
    });

    const btnLaunch = document.getElementById('btn-launch');
    if (btnLaunch) btnLaunch.addEventListener('click', launchProduction);

    const selector = document.getElementById('playlist-selector');
    if (selector) {
        selector.addEventListener('change', () => {
            document.getElementById('current-title').textContent = "Producción: " + selector.value;
        });
    }
}
