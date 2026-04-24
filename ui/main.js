// ATMOS CONTROL CENTER - CORE LOGIC v6.5 (Skill Flow Edition)
document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initVideoAutoplay();
    fetchStats();
    loadRenders();
});

let categoryStats = {};

// GHOST TRIGGER: Activa video al primer toque del usuario (Evita bloqueos de Safari/iOS)
function initVideoAutoplay() {
    const video = document.getElementById('bg-video');
    const startVideo = () => {
        video.play().catch(e => console.log("Autoplay block:", e));
        document.removeEventListener('touchstart', startVideo);
        document.removeEventListener('click', startVideo);
    };
    document.addEventListener('touchstart', startVideo);
    document.addEventListener('click', startVideo);
}

async function fetchStats() {
    try {
        const res = await fetch('/stats');
        if (!res.ok) throw new Error("Stats not available");
        categoryStats = await res.json();
        updateDashboardInfo();
    } catch (e) {
        console.warn("Usando datos de respaldo...");
        categoryStats = { "Paz Interior": 84, "Victoria & Gozo": 45, "Guerra Espiritual": 22 };
        updateDashboardInfo();
    }
}

function updateDashboardInfo() {
    const selector = document.getElementById('playlist-selector');
    const songCountDisplay = document.getElementById('song-count-display');
    const videoPotential = document.getElementById('video-potential');
    const currentTitle = document.getElementById('current-title');
    
    const theme = selector.value;
    const count = categoryStats[theme] || 0;
    
    songCountDisplay.textContent = count;
    videoPotential.textContent = Math.floor(count / 12) + " Videos";
    
    const titles = {
        "Paz Interior": "Atmósfera No Temas",
        "Victoria & Gozo": "Cánticos de Victoria",
        "Guerra Espiritual": "Poder y Fortaleza"
    };
    currentTitle.textContent = titles[theme] || theme;
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
        });
    });

    playlistSelector.addEventListener('change', updateDashboardInfo);

    if (btnLaunch) {
        btnLaunch.addEventListener('click', launchProduction);
    }
}

async function launchProduction() {
    const btn = document.getElementById('btn-launch');
    const statusBadge = document.getElementById('system-status-badge');
    const activeProgress = document.getElementById('active-progress');
    const progressFill = document.querySelector('.progress-fill');
    const progressText = document.querySelector('.progress-text');
    const theme = document.getElementById('playlist-selector').value;

    btn.disabled = true;
    btn.textContent = "EN COLA DE NUBE...";
    statusBadge.textContent = "PROCESANDO";
    statusBadge.classList.add('pulse-glow');

    try {
        const response = await fetch('/run_atmos', { 
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ theme: theme, duration: 3600 })
        });
        
        if (response.ok) {
            statusBadge.textContent = "RENDERIZANDO";
            activeProgress.style.display = "block";
            simulateProgress(progressFill, progressText);
        } else {
            throw new Error();
        }
    } catch (err) {
        alert("⚠️ Error de conexión con Oracle.");
        btn.disabled = false;
        btn.textContent = "REINTENTAR";
    }
}

function simulateProgress(fill, text) {
    let p = 0;
    const interval = setInterval(() => {
        p += Math.random() * 2;
        if (p > 99) {
            p = 99;
            clearInterval(interval);
            text.textContent = "Finalizando renderizado...";
        }
        fill.style.width = p + "%";
        text.textContent = `Progreso: ${Math.floor(p)}%`;
    }, 2000);
}

function loadRenders() {
    const container = document.getElementById('renders-container');
    // Mock data for renders
    const mockRenders = [
        { title: "ATMOS_PAZ_60MIN_8271", date: "Hoy", status: "Listo" },
        { title: "PRODUCCION_OFICIAL_1HORA", date: "Ayer", status: "Listo" }
    ];
    
    container.innerHTML = mockRenders.map(r => `
        <div class="stat-card">
            <span class="label">${r.date}</span>
            <span class="value" style="font-size:0.8rem">${r.title}</span>
            <span class="status-badge" style="margin-top:10px; font-size:0.5rem">${r.status}</span>
        </div>
    `).join('');
}
