const API_BASE = "http://161.153.206.126:5000";

document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    updateSystemStatus();
    loadProductionHistory();
});

async function updateSystemStatus() {
    const badge = document.getElementById('system-status-badge');
    try {
        const res = await fetch(`${API_BASE}/status`);
        const data = await res.json();
        if (data.status === "online") {
            badge.textContent = "CONECTADO";
            badge.style.background = "rgba(0, 255, 127, 0.2)";
            badge.style.color = "#00ff7f";
        }
    } catch (e) {
        badge.textContent = "DESCONECTADO";
        badge.style.background = "rgba(255, 50, 50, 0.2)";
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
            <div class="stat-card" style="grid-column: span 2; border-left: 3px solid var(--accent-color);">
                <div style="display:flex; justify-content:space-between; align-items:start;">
                    <span class="label">${item.timestamp}</span>
                    <div class="status-badge" style="font-size:0.5rem; background: var(--accent-color);">${item.status}</div>
                </div>
                <span class="value" style="font-size:0.8rem; margin-top:5px; display:block;">Tema: ${item.theme}</span>
                <span style="font-size:0.6rem; opacity:0.6; word-break: break-all;">Link: ${item.song_url}</span>
            </div>
        `).join('');
    } catch (e) {
        console.error("Error cargando historial");
    }
}

async function launchProduction() {
    const btn = document.getElementById('btn-launch');
    const songUrlInput = document.getElementById('song-url-input'); // Asegúrate de tener este ID
    const themeSelector = document.getElementById('playlist-selector');
    
    const song_url = songUrlInput ? songUrlInput.value : "https://youtube.com/watch?v=direct";
    const theme = themeSelector.value;

    if (!song_url) {
        alert("Por favor ingresa un link de canción.");
        return;
    }

    // Efecto visual de carga
    btn.disabled = true;
    const originalText = btn.innerHTML;
    btn.innerHTML = '<span class="spinner"></span> ENVIANDO A LA NUBE...';

    try {
        const response = await fetch(`${API_BASE}/process`, { 
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                song_url: song_url, 
                theme: theme 
            })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            alert("🚀 ¡Misión iniciada! GitHub está renderizando tu video. El panel volverá a la normalidad.");
            if (songUrlInput) songUrlInput.value = ""; // Limpiar input
        } else {
            alert("⚠️ Error de GitHub: " + result.message);
        }
    } catch (err) {
        alert("⚠️ El servidor de Oracle no responde. Verifica que esté encendido.");
    } finally {
        // RESET TOTAL: El botón vuelve a la normalidad pase lo que pase
        btn.disabled = false;
        btn.innerHTML = originalText;
        loadProductionHistory(); // Recargar la lista
    }
}

function initNavigation() {
    const navButtons = document.querySelectorAll('.btn-nav');
    const views = document.querySelectorAll('.view');
    const btnLaunch = document.getElementById('btn-launch');
    const playlistSelector = document.getElementById('playlist-selector');

    navButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const viewId = btn.getAttribute('data-view');
            navButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            views.forEach(v => v.classList.remove('active'));
            document.getElementById(viewId).classList.add('active');
            
            if (viewId === 'renders') loadProductionHistory();
        });
    });

    if (btnLaunch) {
        btnLaunch.addEventListener('click', launchProduction);
    }
    
    if (playlistSelector) {
        playlistSelector.addEventListener('change', () => {
            const currentTitle = document.getElementById('current-title');
            if (currentTitle) currentTitle.textContent = "Producción: " + playlistSelector.value;
        });
    }
}
