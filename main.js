// CONFIGURACIÓN MAESTRA
const API_BASE = "http://161.153.206.126:5000";

// ELEMENTOS UI
const btnLaunch = document.getElementById('btn-launch');
const playlistSelector = document.getElementById('playlist-selector');
const durationSelector = document.getElementById('duration-selector');
const styleSelector = document.getElementById('style-selector');
const videoPotential = document.getElementById('video-potential');
const catalogList = document.getElementById('catalog-list');
const historyList = document.getElementById('history-list');
const videoElement = document.querySelector('.video-bg video');

// AUTOMATIC VIDEO PLAYBACK SHIELD
function ensureVideoPlay() {
    if (videoElement) {
        videoElement.play().catch(err => {
            console.log("Autoplay blocked or failed. Trying silent recovery...");
            videoElement.muted = true;
            videoElement.play();
        });
    }
}

// INICIALIZACIÓN
document.addEventListener('DOMContentLoaded', () => {
    loadStats();
    loadCatalog();
    loadHistory();
    ensureVideoPlay();
    
    // Check for Mixed Content issues
    if (window.location.protocol === 'https:' && API_BASE.startsWith('http:')) {
        console.error("⚠️ CRITICAL: Protocol Mismatch. Browsers block HTTPS -> HTTP calls. Dashboard won't work unless Oracle has SSL or you use a proxy.");
        alert("ALERTA DE SEGURIDAD: Tu servidor en Oracle necesita SSL (HTTPS) para funcionar desde esta web segura.");
    }
    
    if (btnLaunch) btnLaunch.addEventListener('click', launchProduction);
    if (playlistSelector) playlistSelector.addEventListener('change', loadStats);
});

async function loadStats() {
    try {
        const res = await fetch(`${API_BASE}/stats`);
        const data = await res.json();
        const theme = playlistSelector.value;
        const isReady = data.ready[theme] || false;
        
        if (isReady) {
            videoPotential.textContent = "LISTO (Playlist Variada)";
            videoPotential.style.color = "#00ff7f";
        } else {
            videoPotential.textContent = "NECESITA MÁS TEMAS";
            videoPotential.style.color = "#ffcc00";
        }
    } catch (e) {
        console.warn("Error stats");
    }
}

async function loadCatalog() {
    try {
        console.log("Solicitando catálogo a:", `${API_BASE}/catalog`);
        const res = await fetch(`${API_BASE}/catalog`);
        if (!res.ok) throw new Error(`HTTP Error: ${res.status}`);
        const catalog = await res.json();
        
        catalogList.innerHTML = catalog.length ? "" : '<p class="empty-msg">No hay canciones disponibles.</p>';
        
        catalog.forEach(song => {
            const item = document.createElement('div');
            item.className = 'catalog-item';
            item.innerHTML = `
                <div class="song-info">
                    <span class="tiny-label">${song.album || 'SIN ÁLBUM'} | ${song.bpm || '??'} BPM</span>
                    <p style="font-weight:700;">${song.title}</p>
                    <span style="font-size:0.6rem; opacity:0.6; color:#f5f0e1;">TEMÁTICA: ${song.theme || 'General'}</span>
                </div>
                <label class="switch">
                    <input type="checkbox" ${song.disabled ? '' : 'checked'} onchange="toggleSong('${song.title}')">
                    <span class="slider"></span>
                </label>
            `;
            catalogList.appendChild(item);
        });
    } catch (err) {
        console.error("Error cargando catálogo:", err);
        catalogList.innerHTML = `<p class="error-msg">⚠️ ERROR DE CONEXIÓN: Verifica que el servidor en Oracle esté corriendo y que permita conexiones desde ${window.location.origin}</p>`;
    }
}

async function toggleSong(title) {
    try {
        await fetch(`${API_BASE}/toggle_song`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ title })
        });
        loadStats();
    } catch (e) { 
        console.error(e);
        alert("Error al actualizar estado."); 
    }
}

async function loadHistory() {
    try {
        const res = await fetch(`${API_BASE}/history`);
        const history = await res.json();
        historyList.innerHTML = history.length ? history.map(item => `
            <div class="item-card">
                <span class="tiny-label">${item.timestamp}</span>
                <p style="font-weight:700; font-size:0.8rem;">${item.theme}</p>
                <div style="font-size:0.5rem; background:var(--accent-blue); padding:2px 8px; border-radius:10px; display:inline-block; margin-top:5px;">${item.status}</div>
            </div>
        `).join('') : "<p style='opacity:0.3; text-align:center;'>Sin historial.</p>";
    } catch (e) { console.error("Error historial"); }
}

async function launchProduction() {
    const url = document.getElementById('song-url-input').value;
    const theme = playlistSelector.value;
    const duration = durationSelector.value;
    const style = styleSelector.value;
    
    if (!url) return alert("Por favor ingresa un link.");

    btnLaunch.disabled = true;
    btnLaunch.textContent = "EN COLA DE NUBE...";

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
