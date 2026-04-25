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
    { id: "Refugio", name: "🛡️ Refugio", type: "pura" },
    { id: "Confianza", name: "⚓ Confianza", type: "pura" },
    { id: "Descanso", name: "🌿 Descanso", type: "pura" },
    { id: "Paz Interior", name: "🌙 Paz Interior", type: "pura" },
    { id: "Intimidad", name: "🕊️ Intimidad", type: "pura" },
    { id: "Poder", name: "👑 Poder", type: "pura" },
    { id: "Restauración", name: "🩹 Restauración", type: "pura" },
    { id: "Avivamiento", name: "🔥 Avivamiento", type: "pura" },
    { id: "Guerra Espiritual", name: "⚔️ Guerra Espiritual", type: "pura" },
    { id: "Victoria & Gozo", name: "🎉 Victoria & Gozo", type: "pura" },
    { id: "Serenidad Profunda", name: "🌊 Serenidad Profunda (Paz + Descanso)", type: "cruce", parts: ["Paz Interior", "Descanso"] },
    { id: "Roca de Salvación", name: "⚓ Roca de Salvación (Refugio + Confianza)", type: "cruce", parts: ["Refugio", "Confianza"] },
    { id: "Presencia Sagrada", name: "✨ Presencia Sagrada (Intimidad + Avivamiento)", type: "cruce", parts: ["Intimidad", "Avivamiento"] },
    { id: "Triunfo Espiritual", name: "🛡️ Triunfo Espiritual (Guerra + Victoria)", type: "cruce", parts: ["Guerra Espiritual", "Victoria & Gozo"] },
    { id: "Gracia Renovadora", name: "💎 Gracia Renovadora (Restauración + Poder)", type: "cruce", parts: ["Restauración", "Poder"] }
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
        const res = await fetch(`https://raw.githubusercontent.com/${GITHUB_USER}/${GITHUB_REPO}/main/data/musichris_master_catalog.json?t=${Date.now()}`);
        masterCatalog = await res.json();
        statTotal.textContent = masterCatalog.length;
        totalSongsBadge.textContent = masterCatalog.length;
        setupAtmosphereSelectors(masterCatalog);
        renderCatalog(masterCatalog);
    } catch (e) {
        console.error("Error cargando catálogo:", e);
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
        s.moments.forEach(m => {
            if (!stats[m]) stats[m] = { total: 0, used: 0 };
            stats[m].total++;
            if (usageHistory.some(h => h.title === s.title && h.atmosphere === m)) stats[m].used++;
        });
    });

    prodTheme.innerHTML = MASTER_ATMOSPHERES.map(atm => {
        let label = atm.name;
        if (atm.type === "pura") {
            const rem = (stats[atm.id]?.total || 0) - (stats[atm.id]?.used || 0);
            label += ` (${rem} nuevas)`;
        }
        return `<option value="${atm.id}">${label}</option>`;
    }).join('');

    catalogFilter.innerHTML = `<option value="all">Ver Todas las Canciones</option>` + 
        MASTER_ATMOSPHERES.filter(a => a.type === "pura").map(a => `<option value="${a.id}">${a.name}</option>`).join('');
}

function renderCatalog(songs) {
    catalogList.innerHTML = '';
    songs.forEach(song => {
        const card = document.createElement('div');
        card.className = 'song-card glass';
        const isSongDisabled = song.disabled === true;
        
        card.innerHTML = `
            <div class="song-info">
                <h4>${song.title}</h4>
                <p>${song.verse} | ${song.bpm} BPM</p>
                <div class="tag-row">${song.moments.map(m => `<span class="tag-mini">${m}</span>`).join('')}</div>
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
    const filtered = val === 'all' ? masterCatalog : masterCatalog.filter(s => s.moments.includes(val));
    renderCatalog(filtered);
}

async function loadHistory() {
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
btnLaunch.onclick = launchProduction;

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
        alert("☁️ Disparador Cloud (GitHub Actions) en desarrollo. Use el motor local por ahora.");
    }
    
    btnLaunch.disabled = false;
    btnLaunch.textContent = "PRODUCIR ATMOS DIAMOND";
}

function switchView(view) {
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    document.getElementById(`view-${view}`).classList.add('active');
    event.currentTarget.classList.add('active');
}

function unlockExperience() {
    document.getElementById('landing-shield').style.display = 'none';
    const bgVideo = document.getElementById('bg-video');
    if (bgVideo) bgVideo.play().catch(e => console.log("Autoplay blocked:", e));
}
