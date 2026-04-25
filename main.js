// CONFIGURACIÓN MAESTRA
const GITHUB_USER = 'hjalmarmeza';
const GITHUB_REPO = 'Musichris_Atmos';
const LOCAL_SERVER = 'http://localhost:5001';

// ELEMENTOS DOM
const prodTheme = document.getElementById('prod-theme');
const durationSelector = document.getElementById('duration-selector');
const btnLaunch = document.getElementById('btn-launch');
const catalogList = document.getElementById('catalog-list');
const catalogFilter = document.getElementById('catalog-filter');
const statTotal = document.getElementById('stat-total');
const totalSongsBadge = document.getElementById('total-songs-badge');
const historyList = document.getElementById('history-list');

let masterCatalog = [];
let isLocalAvailable = false;

// LISTA MAESTRA DE ATMÓSFERAS (10 Puras + 5 Cruces)
const MASTER_ATMOSPHERES = [
    { id: "Refugio", name: "🛡️ Refugio", type: "pura", phrase: "Música para buscar Refugio y Paz" },
    { id: "Confianza", name: "⚓ Confianza", type: "pura", phrase: "Música para fortalecer tu Fe y Confianza" },
    { id: "Descanso", name: "🌿 Descanso", type: "pura", phrase: "Música para un Descanso Profundo" },
    { id: "Paz Interior", name: "🌙 Paz Interior", type: "pura", phrase: "Música para alcanzar Paz Interior" },
    { id: "Intimidad", name: "🕊️ Intimidad", type: "pura", phrase: "Música para orar en Intimidad con Dios" },
    { id: "Poder", name: "👑 Poder", type: "pura", phrase: "Música de Adoración y Poder Celestial" },
    { id: "Restauración", name: "🩹 Restauración", type: "pura", phrase: "Música para Sanar y Restaurar tu Alma" },
    { id: "Avivamiento", name: "🔥 Avivamiento", type: "pura", phrase: "Música para Despertar el Avivamiento" },
    { id: "Guerra Espiritual", name: "⚔️ Guerra Espiritual", type: "pura", phrase: "Música para Vencer en la Batalla" },
    { id: "Victoria & Gozo", name: "🎉 Victoria & Gozo", type: "pura", phrase: "Música de Victoria y Gozo Eterno" },
    { id: "Serenidad Profunda", name: "🌊 Serenidad Profunda", type: "cruce", parts: ["Paz Interior", "Descanso"], phrase: "Música para una Serenidad Profunda" },
    { id: "Roca de Salvación", name: "⚓ Roca de Salvación", type: "cruce", parts: ["Refugio", "Confianza"], phrase: "Música para tu Roca de Salvación" },
    { id: "Presencia Sagrada", name: "✨ Presencia Sagrada", type: "cruce", parts: ["Intimidad", "Avivamiento"], phrase: "Música para entrar en su Presencia Sagrada" },
    { id: "Triunfo Espiritual", name: "🛡️ Triunfo Espiritual", type: "cruce", parts: ["Guerra Espiritual", "Victoria & Gozo"], phrase: "Música para un Triunfo Espiritual" },
    { id: "Gracia Renovadora", name: "💎 Gracia Renovadora", type: "cruce", parts: ["Restauración", "Poder"], phrase: "Música de Gracia Renovadora" }
];

// --- INICIALIZACIÓN ---
document.addEventListener('DOMContentLoaded', async () => {
    await checkLocalServer();
    await loadCatalog();
    await loadHistory();
});

async function checkLocalServer() {
    try {
        const res = await fetch(`${LOCAL_SERVER}/status`);
        isLocalAvailable = res.ok;
    } catch(e) { isLocalAvailable = false; }
}

async function loadCatalog() {
    try {
        const url = `https://raw.githubusercontent.com/${GITHUB_USER}/${GITHUB_REPO}/main/data/musichris_master_catalog.json?t=${Date.now()}`;
        const res = await fetch(url);
        if (!res.ok) throw new Error("Error HTTP " + res.status);
        masterCatalog = await res.json();
        
        statTotal.textContent = masterCatalog.length;
        if (totalSongsBadge) totalSongsBadge.textContent = masterCatalog.length;
        
        setupAtmosphereSelectors(masterCatalog);
        renderCatalog(masterCatalog);
    } catch (e) {
        console.error("Error cargando catálogo:", e);
        if (catalogList) {
            catalogList.innerHTML = `<p class="error-msg" style="color:#ff4d4d; padding:20px; text-align:center; background:rgba(255,0,0,0.1); border-radius:15px; border:1px solid rgba(255,0,0,0.2);">⚠️ ERROR DE CONEXIÓN: No se pudo cargar la biblioteca.<br><small>${e.message}</small></p>`;
        }
    }
}

async function setupAtmosphereSelectors(catalog) {
    let usageHistory = [];
    try {
        const res = await fetch(`https://raw.githubusercontent.com/${GITHUB_USER}/${GITHUB_REPO}/main/data/usage_history.json?t=${Date.now()}`);
        if (res.ok) usageHistory = await res.json();
    } catch(e) {}

    const stats = {};
    catalog.forEach(s => {
        const moments = s.moments || [];
        moments.forEach(m => {
            if (!stats[m]) stats[m] = { total: 0, used: 0 };
            stats[m].total++;
            if (usageHistory.some(h => h.title === s.title && h.atmosphere === m)) stats[m].used++;
        });
    });

    if (prodTheme) {
        prodTheme.innerHTML = MASTER_ATMOSPHERES.map(atm => {
            let label = atm.name;
            if (atm.type === "pura") {
                const total = stats[atm.id]?.total || 0;
                const used = stats[atm.id]?.used || 0;
                const rem = total - used;
                label += ` (${rem} nuevas / ${total} total)`;
            } else if (atm.type === "cruce") {
                // Obtener pool único para el cruce
                const pool = masterCatalog.filter(s => (s.moments || []).some(m => (atm.parts || []).includes(m)));
                label += ` (${pool.length} disponibles)`;
            }
            return `<option value="${atm.id}">${label}</option>`;
        }).join('');

        // Listener para actualizar Preview dinámico
        prodTheme.addEventListener('change', updatePreview);
        updatePreview(); // Inicial
    }

    if (catalogFilter) {
        catalogFilter.innerHTML = `<option value="all">Ver Todas las Canciones</option>` + 
            MASTER_ATMOSPHERES.map(a => `<option value="${a.id}">${a.name}</option>`).join('');
    }
}

function renderCatalog(songs) {
    if (!catalogList) return;
    catalogList.innerHTML = '';
    
    songs.forEach(song => {
        const card = document.createElement('div');
        card.className = 'song-card glass';
        const isSongDisabled = song.disabled === true;
        const verse = song.context?.verse || 'Salmos 23:1';
        const bpm = song.bpm || 'Slow';
        const moments = song.moments || [];
        
        card.innerHTML = `
            <div class="song-info">
                <h4>${song.title}</h4>
                <p>${verse} | ${bpm} BPM</p>
                <div class="tag-row">${moments.map(m => `<span class="tag-mini">${m}</span>`).join('')}</div>
            </div>
            <div class="song-actions">
                <button onclick="toggleSong('${song.title}', ${!isSongDisabled})" class="btn-mini ${isSongDisabled ? 'btn-enable' : 'btn-disable'}">
                    ${isSongDisabled ? 'HABILITAR' : 'DESACTIVAR'}
                </button>
            </div>
        `;
        catalogList.appendChild(card);
    });
}

function filterCatalog() {
    const val = catalogFilter.value;
    const filtered = val === 'all' ? masterCatalog : masterCatalog.filter(s => (s.moments || []).includes(val));
    renderCatalog(filtered);
}

async function loadHistory() {
    if (!historyList) return;
    try {
        const res = await fetch(`https://raw.githubusercontent.com/${GITHUB_USER}/${GITHUB_REPO}/main/data/usage_history.json?t=${Date.now()}`);
        if (!res.ok) return;
        const history = await res.json();
        historyList.innerHTML = history.reverse().slice(0, 10).map(h => `
            <div class="history-item glass">
                <div class="hist-icon">🎬</div>
                <div class="hist-details">
                    <strong>${h.atmosphere}</strong>
                    <span>${h.title}</span>
                </div>
                <div class="hist-date">${h.date.split(' ')[0]}</div>
            </div>
        `).join('');
    } catch(e) {}
}

// --- ACCIONES ---
if (btnLaunch) btnLaunch.onclick = launchProduction;

async function launchProduction() {
    const selectedId = prodTheme.value;
    const atm = MASTER_ATMOSPHERES.find(a => a.id === selectedId);
    const duration = durationSelector.value;
    
    let theme1 = selectedId;
    let theme2 = "none";

    if (atm && atm.type === "cruce") {
        theme1 = atm.parts[0];
        theme2 = atm.parts[1];
    }

    btnLaunch.disabled = true;
    btnLaunch.textContent = "PROCESANDO...";

    if (isLocalAvailable) {
        try {
            const res = await fetch(`${LOCAL_SERVER}/run_atmos`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ theme: theme1, theme2: theme2, duration: parseInt(duration) })
            });
            if (res.ok) alert(`🚀 Diamond Engine Activado: ${selectedId}`);
            else alert("❌ Error en el motor local.");
        } catch(e) { alert("⚠️ Error de conexión local."); }
    } else {
        const ghToken = localStorage.getItem('GH_PAT') || prompt("Introduce tu GitHub Personal Access Token (PAT) para lanzar en la nube:");
        if (!ghToken) return alert("Se requiere un Token para la producción Cloud.");
        localStorage.setItem('GH_PAT', ghToken);

        const repoOwner = "hjalmarmeza";
        const repoName = "Musichris_Atmos";

        try {
            const response = await fetch(`https://api.github.com/repos/${repoOwner}/${repoName}/dispatches`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${ghToken}`,
                    'Accept': 'application/vnd.github.v3+json',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    event_type: 'run-atmos',
                    client_payload: {
                        duration: parseInt(durationSelector.value),
                        theme: prodTheme.value
                    }
                })
            });

            if (response.ok) {
                alert(`🚀 ORDEN ENVIADA A GITHUB ACTIONS\nAtmósfera: ${prodTheme.value}\nDuración: ${durationSelector.value}s\n\nEl renderizado comenzará en unos segundos en la nube.`);
            } else {
                const err = await response.json();
                alert(`❌ Error en el disparador Cloud: ${err.message}`);
            }
        } catch (error) {
            alert("❌ Error de conexión con GitHub API.");
        }
    }
    
    btnLaunch.disabled = false;
    btnLaunch.textContent = "PRODUCIR ATMOS DIAMOND";
}

function updatePreview() {
    const selectedId = prodTheme.value;
    const atm = MASTER_ATMOSPHERES.find(a => a.id === selectedId);
    if (!atm) return;

    const displayTitle = document.getElementById('preview-text-title');
    const mainDisplay = document.getElementById('display-theme');

    if (displayTitle) displayTitle.textContent = atm.phrase.toUpperCase();
    if (mainDisplay) mainDisplay.textContent = `Atmos: ${atm.id}`;
}

// Global para los botones de desactivar
window.toggleSong = toggleSong;
window.switchView = switchView;
window.filterCatalog = filterCatalog;

function switchView(view) {
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    const target = document.getElementById(`view-${view}`);
    if (target) target.classList.add('active');
    if (event && event.currentTarget) event.currentTarget.classList.add('active');
}

function unlockExperience() {
    const shield = document.getElementById('landing-shield');
    if (shield) shield.style.display = 'none';
    const bgVideo = document.getElementById('bg-video');
    if (bgVideo) bgVideo.play().catch(e => console.log("Autoplay blocked:", e));
}
