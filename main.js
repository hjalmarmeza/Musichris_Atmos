// CONFIGURACIÓN SERVERLESS (V7.2)
const GITHUB_REPO = "hjalmarmeza/Musichris_Atmos";
const CATALOG_PATH = "data/musichris_master_catalog.json";
const DISABLED_PATH = "data/disabled_songs.json";
const HISTORY_PATH = "data/production_history.json";

// ELEMENTOS UI
const btnLaunch = document.getElementById('btn-launch');
const playlistSelector = document.getElementById('playlist-selector');
const durationSelector = document.getElementById('duration-selector');
const videoPotential = document.getElementById('video-potential');
const catalogList = document.getElementById('catalog-list');
const historyList = document.getElementById('history-list');
const videoElement = document.getElementById('bg-video');

// MODAL SETTINGS
const modalSettings = document.getElementById('modal-settings');
const btnSettings = document.getElementById('btn-settings');
const btnCloseModal = document.getElementById('btn-close-modal');
const btnSaveToken = document.getElementById('btn-save-token');
const inputToken = document.getElementById('github-token-input');

let GITHUB_TOKEN = localStorage.getItem('gh_token') || "";

// --- SISTEMA DE COMUNICACIÓN GITHUB ---

async function ghFetch(path, options = {}) {
    if (!GITHUB_TOKEN) {
        modalSettings.classList.add('active');
        throw new Error("Token requerido");
    }

    const url = `https://api.github.com/repos/${GITHUB_REPO}/${path}`;
    const defaultHeaders = {
        'Authorization': `token ${GITHUB_TOKEN}`,
        'Accept': 'application/vnd.github.v3+json'
    };

    const response = await fetch(url, {
        ...options,
        headers: { ...defaultHeaders, ...options.headers }
    });

    if (response.status === 401) {
        localStorage.removeItem('gh_token');
        alert("⚠️ Token inválido. Por favor configúralo de nuevo.");
        modalSettings.classList.add('active');
    }

    return response;
}

// --- LÓGICA DE DATOS ---

async function loadData() {
    try {
        // Cargar Catálogo (Estático)
        const resCat = await fetch(`https://raw.githubusercontent.com/${GITHUB_REPO}/main/${CATALOG_PATH}`);
        const catalog = await resCat.json();

        // Cargar Desactivadas (Dinámico vía API para evitar cache)
        let disabled = [];
        try {
            const resDis = await fetch(`https://raw.githubusercontent.com/${GITHUB_REPO}/main/${DISABLED_PATH}?t=${Date.now()}`);
            disabled = await resDis.json();
        } catch(e) { console.warn("Usando lista vacía."); }

        renderCatalog(catalog, disabled);
        updatePotential(catalog, disabled);
        loadHistory();
    } catch (err) {
        console.error("Error cargando datos:", err);
        catalogList.innerHTML = `<p class='error-msg'>⚠️ ERROR: No se pudo cargar el catálogo. Verifica tu conexión.</p>`;
    }
}

function renderCatalog(catalog, disabled) {
    catalogList.innerHTML = "";
    catalog.forEach(song => {
        const isDisabled = disabled.includes(song.title);
        const item = document.createElement('div');
        item.className = `item-card ${isDisabled ? 'disabled' : ''}`;
        item.style.display = "flex";
        item.style.justifyContent = "space-between";
        item.style.alignItems = "center";
        item.style.opacity = isDisabled ? "0.4" : "1";

        item.innerHTML = `
            <div>
                <p style="font-weight:700; font-size:0.9rem;">${song.title}</p>
                <p style="font-size:0.6rem; opacity:0.6;">${song.artist} | ${song.duration}</p>
            </div>
            <label class="switch">
                <input type="checkbox" ${isDisabled ? '' : 'checked'} onchange="toggleSong('${song.title}')">
                <span class="slider"></span>
            </label>
        `;
        catalogList.appendChild(item);
    });
}

async function toggleSong(title) {
    if (!GITHUB_TOKEN) return modalSettings.classList.add('active');

    try {
        // 1. Obtener archivo actual y su SHA
        const res = await ghFetch(`contents/${DISABLED_PATH}`);
        const fileData = await res.json();
        const currentList = JSON.parse(atob(fileData.content));
        const sha = fileData.sha;

        // 2. Modificar lista
        let newList;
        if (currentList.includes(title)) {
            newList = currentList.filter(t => t !== title);
        } else {
            newList = [...currentList, title];
        }

        // 3. Subir a GitHub
        await ghFetch(`contents/${DISABLED_PATH}`, {
            method: 'PUT',
            body: JSON.stringify({
                message: `Update disabled songs: ${title}`,
                content: btoa(JSON.stringify(newList, null, 2)),
                sha: sha
            })
        });

        loadData();
    } catch (e) {
        console.error(e);
        alert("Error al actualizar estado en la nube.");
    }
}

async function loadHistory() {
    try {
        const res = await fetch(`https://raw.githubusercontent.com/${GITHUB_REPO}/main/${HISTORY_PATH}?t=${Date.now()}`);
        const history = await res.json();
        historyList.innerHTML = history.length ? history.reverse().slice(0, 10).map(item => `
            <div class="item-card">
                <span class="tiny-label">${item.timestamp}</span>
                <p style="font-weight:700; font-size:0.8rem;">${item.theme}</p>
                <div style="font-size:0.5rem; background:var(--accent-blue); padding:2px 8px; border-radius:10px; display:inline-block; margin-top:5px;">${item.status}</div>
            </div>
        `).join('') : "<p style='opacity:0.3; text-align:center;'>Sin historial.</p>";
    } catch (e) { console.error("Error historial"); }
}

function updatePotential(catalog, disabled) {
    const active = catalog.filter(s => !disabled.includes(s.title)).length;
    videoPotential.textContent = `${active} VIDEOS LISTOS`;
    videoPotential.style.color = active > 50 ? "#00ff7f" : "#ffcc00";
}

async function launchProduction() {
    if (!GITHUB_TOKEN) return modalSettings.classList.add('active');

    const theme = playlistSelector.value;
    const duration = durationSelector.value;

    btnLaunch.disabled = true;
    btnLaunch.textContent = "DISPARANDO NUBE...";

    try {
        const response = await ghFetch('dispatches', {
            method: 'POST',
            body: JSON.stringify({
                event_type: "launch_atmos",
                client_payload: {
                    theme: theme,
                    duration: parseInt(duration),
                    version: "7.0 Serverless"
                }
            })
        });

        if (response.status === 204) {
            alert("🚀 ¡MISIÓN LANZADA! La producción ha comenzado en los servidores de GitHub.");
            // Opcional: Registrar en historial local antes de que el bot lo haga oficial
        } else {
            alert("❌ GitHub rechazó la orden. Revisa el Token.");
        }
    } catch (err) {
        console.error(err);
    } finally {
        btnLaunch.disabled = false;
        btnLaunch.textContent = "INICIAR PRODUCCIÓN V7.0";
    }
}

// --- EVENTOS Y UI ---

btnSettings.onclick = () => modalSettings.classList.add('active');
btnCloseModal.onclick = () => modalSettings.classList.remove('active');
btnSaveToken.onclick = () => {
    const val = inputToken.value.trim();
    if (val) {
        localStorage.setItem('gh_token', val);
        GITHUB_TOKEN = val;
        modalSettings.classList.remove('active');
        alert("🔑 Token guardado localmente.");
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

// INIT
window.onload = () => {
    ensureVideoPlay();
    loadData();
    if (GITHUB_TOKEN) inputToken.value = GITHUB_TOKEN;
};
