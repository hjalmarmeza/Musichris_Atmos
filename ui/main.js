// CONFIGURACIÓN SERVERLESS ATMOS v8.12
const GITHUB_REPO = "hjalmarmeza/Musichris_Atmos";
const CATALOG_PATH = "data/musichris_master_catalog.json";
const DISABLED_PATH = "data/disabled_songs.json";
const HISTORY_PATH = "data/production_history.json";

// ELEMENTOS UI
const btnLaunch = document.getElementById('btn-launch');
const playlistSelector = document.getElementById('playlist-selector');
const durationSelector = document.getElementById('duration-selector');
const displayTheme = document.getElementById('display-theme');
const catalogList = document.getElementById('catalog-list');
const historyList = document.getElementById('history-list');
const prodTheme = document.getElementById('prod-theme');
const prodTheme2 = document.getElementById('prod-theme-2');
const catalogFilter = document.getElementById('catalog-filter');
const totalSongsBadge = document.getElementById('total-songs-badge');
const statTotal = document.getElementById('stat-total');
const statFiltered = document.getElementById('stat-filtered');

let masterCatalog = [];
const modalSettings = document.getElementById('modal-settings');
const btnSettings = document.getElementById('btn-settings');
const btnCloseModal = document.getElementById('btn-close-modal');
const btnSaveToken = document.getElementById('btn-save-token');
const inputToken = document.getElementById('github-token-input');

let GITHUB_TOKEN = localStorage.getItem('gh_token') || "";

// --- SISTEMA DE COMUNICACIÓN GITHUB ---

async function ghFetch(path, options = {}) {
    if (!GITHUB_TOKEN && (options.method === 'POST' || options.method === 'PUT')) {
        modalSettings.classList.add('active');
        throw new Error("Token requerido para esta acción.");
    }

    const url = `https://api.github.com/repos/${GITHUB_REPO}/${path}`;
    const headers = {
        'Accept': 'application/vnd.github.v3+json',
        ...(GITHUB_TOKEN ? { 'Authorization': `token ${GITHUB_TOKEN}` } : {})
    };

    const response = await fetch(url, {
        ...options,
        headers: { ...headers, ...options.headers }
    });

    if (response.status === 401) {
        localStorage.removeItem('gh_token');
        modalSettings.classList.add('active');
    }

    return response;
}

// --- LÓGICA DE DATOS ---

async function loadData() {
    try {
        // Cargar Catálogo (Desde Raw para mayor velocidad en lectura)
        const resCat = await fetch(`https://raw.githubusercontent.com/${GITHUB_REPO}/main/${CATALOG_PATH}?t=${Date.now()}`);
        const catalog = await resCat.json();
        masterCatalog = catalog;

        // Cargar Desactivadas
        let disabled = [];
        try {
            const resDis = await fetch(`https://raw.githubusercontent.com/${GITHUB_REPO}/main/${DISABLED_PATH}?t=${Date.now()}`);
            if (resDis.ok) disabled = await resDis.json();
        } catch(e) { console.warn("Usando lista vacía."); }

        renderCatalog(catalog, disabled);
        updatePreview(catalog);
        setupAtmosphereSelectors(catalog);
        loadHistory();
    } catch (err) {
        console.error("Error cargando datos:", err);
        catalogList.innerHTML = `<p class='error-msg'>⚠️ ERROR DE CONEXIÓN: No se pudo cargar la biblioteca.</p>`;
    }
}

function renderCatalog(catalog, disabled) {
    if (!catalog.length) {
        catalogList.innerHTML = "<p style='text-align:center; opacity:0.5;'>Biblioteca vacía.</p>";
        return;
    }

    catalogList.innerHTML = "";
    catalog.forEach(song => {
        const isDisabled = disabled.includes(song.title);
        const item = document.createElement('div');
        item.className = 'item-card';
        item.style.display = "flex";
        item.style.justifyContent = "space-between";
        item.style.alignItems = "center";
        item.style.opacity = isDisabled ? "0.3" : "1";

        item.innerHTML = `
            <div>
                <p style="font-weight:700; font-size:0.9rem;">${song.title}</p>
                <p style="font-size:0.6rem; opacity:0.6; margin-top:3px;">${song.artist || 'MusiChris Studio'}</p>
            </div>
            <label class="switch">
                <input type="checkbox" ${isDisabled ? '' : 'checked'} onchange="toggleSong('${song.title}')">
                <span class="slider"></span>
            </label>
        `;
        catalogList.appendChild(item);
    });
    
    // Update stats
    totalSongsBadge.textContent = masterCatalog.length;
    statTotal.textContent = masterCatalog.length;
    statFiltered.textContent = filtered.length;
}

function setupAtmosphereSelectors(catalog) {
    const stats = {};
    catalog.forEach(s => {
        s.moments.forEach(m => {
            stats[m] = (stats[m] || 0) + 1;
        });
    });

    // Filtramos atmósferas con 0 canciones
    const activeThemes = Object.keys(stats).filter(t => stats[t] > 0);
    
    // Actualizar Select de Producción
    const options = activeThemes.map(t => `<option value="${t}">${t} (${stats[t]} temas)</option>`).join('');
    prodTheme.innerHTML = options;
    prodTheme2.innerHTML = '<option value="none">Sin Cruce (Atmósfera Única)</option>' + options;
    
    // Actualizar Filtro de Catálogo
    catalogFilter.innerHTML = `<option value="all">Ver Todas (${catalog.length})</option>` + 
        activeThemes.map(t => `<option value="${t}">${t} (${stats[t]})</option>`).join('');
}

function filterCatalog() {
    const val = catalogFilter.value;
    renderCatalog(masterCatalog, [], val);
}

function updatePreview(catalog) {
    if (!catalog.length) return;
    
    // Paisajes disponibles (Hardcoded based on the assets folder)
    const landscapes = [
        "atardecer_sereno.jpg",
        "bosque_niebla.jpg",
        "montana_glacial.jpg",
        "oceano_profundo.jpg",
        "pradera_oro.jpg",
        "valle_estrellado.jpg"
    ];

    let currentIndex = 0;
    
    function cycle() {
        const song = catalog[Math.floor(Math.random() * catalog.length)];
        const landscape = landscapes[Math.floor(Math.random() * landscapes.length)];
        
        previewLandscape.src = `assets/Paisajes/${landscape}`;
        previewTitle.textContent = song.title;
        previewVerse.textContent = song.verse || "MusiChris Studio";
        
        setTimeout(cycle, 5000);
    }
    
    cycle();
}

async function toggleSong(title) {
    if (!GITHUB_TOKEN) return modalSettings.classList.add('active');

    try {
        const res = await ghFetch(`contents/${DISABLED_PATH}`);
        const fileData = await res.json();
        const currentList = JSON.parse(atob(fileData.content));
        const sha = fileData.sha;

        let newList = currentList.includes(title) 
            ? currentList.filter(t => t !== title) 
            : [...currentList, title];

        await ghFetch(`contents/${DISABLED_PATH}`, {
            method: 'PUT',
            body: JSON.stringify({
                message: `Admin: Toggle ${title}`,
                content: btoa(JSON.stringify(newList, null, 2)),
                sha: sha
            })
        });

        loadData();
    } catch (e) { alert("Error al sincronizar con GitHub."); }
}

async function loadHistory() {
    try {
        const res = await fetch(`https://raw.githubusercontent.com/${GITHUB_REPO}/main/${HISTORY_PATH}?t=${Date.now()}`);
        const history = await res.json();
        
        historyList.innerHTML = history.length ? history.reverse().slice(0, 15).map(item => {
            const dateLabel = isToday(item.timestamp) ? "Hoy" : "Ayer";
            return `
                <div class="item-card">
                    <p style="font-size:0.65rem; opacity:0.5; margin-bottom:5px;">${dateLabel} • ${item.timestamp.split(' ')[1] || ''}</p>
                    <p style="font-weight:700; font-size:0.85rem; letter-spacing:0.5px;">${item.theme.toUpperCase()}</p>
                    <div style="margin-top:12px; display:flex; justify-content:space-between; align-items:center;">
                        <span class="badge-ready">Listo</span>
                        <span style="font-size:0.5rem; opacity:0.3;">#${item.id || 'N/A'}</span>
                    </div>
                </div>
            `;
        }).join('') : "<p style='opacity:0.3; text-align:center;'>Sin producciones recientes.</p>";
    } catch (e) { console.error("Error historial"); }
}

function isToday(timestamp) {
    const today = new Date().toLocaleDateString();
    return timestamp.includes(today);
}

async function launchProduction() {
    if (!GITHUB_TOKEN) return modalSettings.classList.add('active');

    const theme = playlistSelector.value;
    const duration = durationSelector.value;

    btnLaunch.disabled = true;
    btnLaunch.style.opacity = "0.5";
    btnLaunch.textContent = "DISPARANDO NUBE...";

    try {
        const response = await ghFetch('dispatches', {
            method: 'POST',
            body: JSON.stringify({
                event_type: "launch_atmos",
                client_payload: {
                    theme: theme,
                    duration: parseInt(duration),
                    version: "8.12 Serverless"
                }
            })
        });

        if (response.status === 204) {
            alert("🚀 ¡MISIÓN LANZADA! Producción iniciada en GitHub.");
        } else {
            alert("❌ GitHub rechazó la orden. Revisa el Token.");
        }
    } catch (err) {
        alert("Error de red con GitHub.");
    } finally {
        btnLaunch.disabled = false;
        btnLaunch.style.opacity = "1";
        btnLaunch.textContent = "INICIAR PRODUCCIÓN V7.0";
    }
}

// --- EVENTOS ---

playlistSelector.onchange = () => {
    displayTheme.textContent = `Producción: ${playlistSelector.value}`;
};

btnSettings.onclick = () => modalSettings.classList.add('active');
btnCloseModal.onclick = () => modalSettings.classList.remove('active');
btnSaveToken.onclick = () => {
    const val = inputToken.value.trim();
    if (val) {
        localStorage.setItem('gh_token', val);
        GITHUB_TOKEN = val;
        modalSettings.classList.remove('active');
        loadData();
    }
};

// Navegación
document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.onclick = () => {
        document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
        btn.classList.add('active');
        document.getElementById(`view-${btn.dataset.view}`).classList.add('active');
    };
});

// Autoplay Shield
function ensureVideoPlay() {
    if (videoElement) {
        videoElement.muted = true;
        videoElement.play().catch(() => {
            document.addEventListener('mousedown', () => videoElement.play(), { once: true });
        });
    }
}

// UNLOCK EXPERIENCE (FOR AUTOPLAY)
function unlockExperience() {
    const shield = document.getElementById('landing-shield');
    if (shield) {
        shield.classList.add('hidden');
        if (videoElement) {
            videoElement.play().catch(e => console.log("Fallo final:", e));
        }
        // Small delay to ensure smooth transition
        setTimeout(() => shield.style.display = 'none', 1000);
    }
}

// INIT
window.onload = () => {
    // Initial attempt (some browsers might allow it)
    if (videoElement) {
        videoElement.muted = true;
        videoElement.play().catch(() => {
            console.log("🛡️ Escudo de interacción activo.");
        });
    }
    loadData();
    if (GITHUB_TOKEN) inputToken.value = GITHUB_TOKEN;
};
