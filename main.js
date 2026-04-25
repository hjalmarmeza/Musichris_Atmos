const GITHUB_REPO = "hjalmarmeza/Musichris_Atmos";
const CATALOG_PATH = "data/musichris_master_catalog.json";
const DISABLED_PATH = "data/disabled_songs.json";
const HISTORY_PATH = "data/production_history.json";
const LOCAL_SERVER = "http://localhost:8080";

// ELEMENTOS UI
const btnLaunch = document.getElementById('btn-launch');
const durationSelector = document.getElementById('duration-selector');
const prodTheme = document.getElementById('prod-theme');
const prodTheme2 = document.getElementById('prod-theme-2');
const catalogFilter = document.getElementById('catalog-filter');
const totalSongsBadge = document.getElementById('total-songs-badge');
const statTotal = document.getElementById('stat-total');
const statFiltered = document.getElementById('stat-filtered');
const catalogList = document.getElementById('catalog-list');
const historyList = document.getElementById('history-list');
const videoElement = document.getElementById('bg-video');
const previewLandscape = document.getElementById('preview-landscape');
const previewTitle = document.getElementById('preview-text-title');
const previewVerse = document.getElementById('preview-text-verse');

// ESTADO GLOBAL
let masterCatalog = [];
let isLocalAvailable = false;
let GITHUB_TOKEN = localStorage.getItem('gh_token') || "";

// MODAL SETTINGS
const modalSettings = document.getElementById('modal-settings');
const btnSettings = document.getElementById('btn-settings');
const btnCloseModal = document.getElementById('btn-close-modal');
const btnSaveToken = document.getElementById('btn-save-token');
const inputToken = document.getElementById('github-token-input');

// --- SISTEMA DE COMUNICACIÓN ---

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
        } catch(e) { console.warn("Usando lista vacía de desactivadas."); }

        renderCatalog(catalog, disabled);
        setupAtmosphereSelectors(catalog);
        updatePreview(catalog);
        loadHistory();
        checkLocalServer();
    } catch (err) {
        console.error("Error cargando datos:", err);
        catalogList.innerHTML = `<p class='error-msg'>⚠️ ERROR DE CONEXIÓN: No se pudo cargar la biblioteca.</p>`;
    }
}

function renderCatalog(catalog, disabled = [], filter = 'all') {
    catalogList.innerHTML = "";
    
    const filtered = filter === 'all' 
        ? catalog 
        : catalog.filter(s => s.moments.includes(filter));

    filtered.forEach(song => {
        const isSongDisabled = disabled.includes(song.title);
        const card = document.createElement('div');
        card.className = `item-card glass ${isSongDisabled ? 'disabled' : ''}`;
        card.innerHTML = `
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <h4 style="color:#C5A059;">${song.title}</h4>
                    <p style="font-size:0.7rem; opacity:0.6;">${song.theme || 'Sin tema'}</p>
                </div>
                <button onclick="toggleSong('${song.title}', ${!isSongDisabled})" class="btn-mini">
                    ${isSongDisabled ? 'HABILITAR' : 'DESACTIVAR'}
                </button>
            </div>
        `;
        catalogList.appendChild(card);
    });

    // Actualizar badges
    totalSongsBadge.textContent = catalog.length;
    statTotal.textContent = catalog.length;
    statFiltered.textContent = filtered.length;
}

async function setupAtmosphereSelectors(catalog) {
    // Cargar historial para estadísticas
    let usageHistory = [];
    try {
        const res = await fetch(`https://raw.githubusercontent.com/${GITHUB_REPO}/main/data/usage_history.json?t=${Date.now()}`);
        if (res.ok) usageHistory = await res.json();
    } catch(e) {}

    const stats = {};
    catalog.forEach(s => {
        s.moments.forEach(m => {
            if (!stats[m]) stats[m] = { total: 0, used: 0 };
            stats[m].total++;
            if (usageHistory.some(h => h.title === s.title && h.atmosphere === m)) {
                stats[m].used++;
            }
        });
    });

    const activeThemes = Object.keys(stats).sort();
    
    // Select de Producción
    prodTheme.innerHTML = activeThemes.map(t => {
        const remaining = stats[t].total - stats[t].used;
        const statusIcon = remaining === 0 ? '⚠️' : '🟢';
        return `<option value="${t}">${statusIcon} ${t} (${remaining} nuevas / ${stats[t].total} tot)</option>`;
    }).join('');

    prodTheme2.innerHTML = '<option value="none">Sin Cruce (Atmósfera Única)</option>' + 
        activeThemes.map(t => `<option value="${t}">${t}</option>`).join('');
    
    // Sugerencia Inteligente al cambiar
    prodTheme.onchange = () => {
        const theme = prodTheme.value;
        const remaining = stats[theme].total - stats[theme].used;
        if (remaining === 0) {
            const suggestion = getSmartSuggestion(theme);
            alert(`🛡️ [INVENTARIO AGOTADO] No quedan canciones nuevas en "${theme}".\n\n💡 SUGERENCIA DIAMOND: Prueba el cruce "${suggestion.name}" para reutilizar contenido con una nueva esencia.`);
            prodTheme2.value = suggestion.partner;
        }
    };

    // Filtro de Catálogo
    catalogFilter.innerHTML = `<option value="all">Ver Todas (${catalog.length})</option>` + 
        activeThemes.map(t => `<option value="${t}">${t} (${stats[t].total})</option>`).join('');
}

function getSmartSuggestion(theme) {
    const suggestions = {
        "Refugio": { name: "Roca de Salvación", partner: "Confianza" },
        "Confianza": { name: "Roca de Salvación", partner: "Refugio" },
        "Descanso": { name: "Serenidad Profunda", partner: "Paz Interior" },
        "Paz Interior": { name: "Serenidad Profunda", partner: "Descanso" },
        "Intimidad": { name: "Presencia Sagrada", partner: "Avivamiento" },
        "Avivamiento": { name: "Presencia Sagrada", partner: "Intimidad" },
        "Guerra Espiritual": { name: "Triunfo Espiritual", partner: "Victoria & Gozo" },
        "Victoria & Gozo": { name: "Triunfo Espiritual", partner: "Guerra Espiritual" }
    };
    return suggestions[theme] || { name: "Mezcla General", partner: "all" };
}


function filterCatalog() {
    renderCatalog(masterCatalog, [], catalogFilter.value);
}

function updatePreview(catalog) {
    if (!catalog.length) return;
    
    const landscapes = [
        "atardecer_sereno.jpg", "bosque_niebla.jpg", "montana_glacial.jpg",
        "oceano_profundo.jpg", "pradera_oro.jpg", "valle_estrellado.jpg"
    ];

    function cycle() {
        const song = catalog[Math.floor(Math.random() * catalog.length)];
        const landscape = landscapes[Math.floor(Math.random() * landscapes.length)];
        
        previewLandscape.src = `assets/Paisajes/${landscape}`;
        previewTitle.textContent = song.title;
        previewVerse.textContent = song.verse || "MusiChris Studio";
        
        setTimeout(cycle, 6000);
    }
    cycle();
}

async function loadHistory() {
    try {
        const res = await fetch(`https://raw.githubusercontent.com/${GITHUB_REPO}/main/${HISTORY_PATH}?t=${Date.now()}`);
        if (!res.ok) throw new Error();
        const history = await res.json();
        
        historyList.innerHTML = history.map(h => `
            <div class="item-card glass" style="border-left: 3px solid #C5A059;">
                <p style="font-weight:700;">${h.theme}</p>
                <p style="font-size:0.7rem; opacity:0.5;">${h.timestamp} • ${Math.floor(h.duration/60)}min</p>
            </div>
        `).join('') || "<p class='loading-msg'>No hay historial disponible.</p>";
    } catch(e) {
        historyList.innerHTML = "<p class='loading-msg'>No se pudo cargar el historial.</p>";
    }
}

// --- ACCIONES ---

async function launchProduction() {
    const theme = prodTheme.value;
    const theme2 = prodTheme2.value;
    const duration = durationSelector.value;
    
    const finalTheme = theme2 === 'none' ? theme : `${theme} & ${theme2}`;

    btnLaunch.disabled = true;
    btnLaunch.style.opacity = "0.5";
    btnLaunch.textContent = "PROCESANDO...";

    // 1. Intentar Local
    if (isLocalAvailable) {
        try {
            const res = await fetch(`${LOCAL_SERVER}/run_atmos`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ theme: finalTheme, duration: parseInt(duration) })
            });
            if (res.ok) {
                alert(`🚀 [LOCAL] Diamond Engine Activado: ${finalTheme}`);
                return finalizeLaunch();
            }
        } catch (e) { console.warn("Fallo local, intentando nube..."); }
    }

    // 2. Fallback Nube (GitHub Dispatch)
    if (!GITHUB_TOKEN) {
        modalSettings.classList.add('active');
        finalizeLaunch();
        return;
    }

    try {
        const res = await fetch(`https://api.github.com/repos/${GITHUB_REPO}/dispatches`, {
            method: 'POST',
            headers: {
                'Authorization': `token ${GITHUB_TOKEN}`,
                'Accept': 'application/vnd.github.v3+json'
            },
            body: JSON.stringify({
                event_type: "atmos_render",
                client_payload: { theme: finalTheme, duration: parseInt(duration), version: "10.1 Diamond" }
            })
        });

        if (res.status === 204) {
            alert("🚀 [CLOUD] Misión Diamond Lanzada a GitHub Actions.");
        } else {
            alert("❌ Error al contactar la nube: " + res.status);
        }
    } catch (e) {
        alert("❌ Error de red: " + e.message);
    }
    
    finalizeLaunch();
}

function finalizeLaunch() {
    btnLaunch.disabled = false;
    btnLaunch.style.opacity = "1";
    btnLaunch.textContent = "PRODUCIR ATMOS DIAMOND";
}

async function checkLocalServer() {
    try {
        const res = await fetch(`${LOCAL_SERVER}/check_status`);
        if (res.ok) {
            isLocalAvailable = true;
            const badge = document.querySelector('.badge-status');
            badge.textContent = "DIAMOND ENGINE LOCAL ACTIVO";
            badge.style.background = "linear-gradient(90deg, #C5A059, #FFD700)";
            console.log("💎 Diamond Engine Local detectado.");
        }
    } catch (e) {
        console.log("☁️ Modo Cloud (No se detectó servidor local).");
    }
}

// --- UI HELPERS ---

function switchView(viewId) {
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    
    document.getElementById(`view-${viewId}`).classList.add('active');
    const activeBtn = Array.from(document.querySelectorAll('.nav-btn')).find(b => b.textContent.includes(viewId.toUpperCase()));
    if (activeBtn) activeBtn.classList.add('active');
}

function unlockExperience() {
    document.getElementById('landing-shield').classList.add('hidden');
    if (videoElement) videoElement.play().catch(e => console.warn("Autoplay bloqueado"));
}

// Eventos
btnLaunch.onclick = launchProduction;
btnSettings.onclick = () => modalSettings.classList.add('active');
btnCloseModal.onclick = () => modalSettings.classList.remove('active');
btnSaveToken.onclick = () => {
    localStorage.setItem('gh_token', inputToken.value);
    GITHUB_TOKEN = inputToken.value;
    modalSettings.classList.remove('active');
    alert("Token Guardado.");
};

// Inicializar
window.onload = loadData;
