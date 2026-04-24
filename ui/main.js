// ATMOS CONTROL CENTER - CORE LOGIC
document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    loadDashboardData();
    loadCatalog();
    loadRenders();
    initVideoAutoplay();
});

function initVideoAutoplay() {
    const video = document.getElementById('bg-video');
    // Forzar reproducción al primer clic en cualquier lugar
    document.addEventListener('click', () => {
        if (video.paused) video.play();
    }, { once: true });
}

function initNavigation() {
    const navButtons = document.querySelectorAll('.btn-nav');
    const views = document.querySelectorAll('.view');
    const btnLaunch = document.getElementById('btn-launch');
    const activeProgress = document.getElementById('active-progress');
    const progressFill = document.querySelector('.progress-fill');
    const progressText = document.querySelector('.progress-text');
    const currentTitle = document.getElementById('current-title');
    const statusBadge = document.querySelector('.status-badge');

    navButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const viewId = btn.getAttribute('data-view');
            navButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            views.forEach(v => v.classList.remove('active'));
            document.getElementById(viewId).classList.add('active');
        });
    });

    // Lógica del Botón de Lanzamiento
    if (btnLaunch) {
        const playlistSelector = document.getElementById('playlist-selector');
        const renderEst = document.getElementById('render-est');
        const songCountDisplay = document.getElementById('song-count-display');
        const videoPotential = document.getElementById('video-potential');

        const categoryData = {
            paz: { songs: 84, title: "No Temas: Yo estoy contigo en medio del valle", est: 3.2 },
            fortaleza: { songs: 44, title: "Poder Infinito: Tu Victoria está en Dios", est: 2.8 },
            reflexion: { songs: 11, title: "Selah: Momentos de Intimidad con el Padre", est: 1.5 }
        };

        // Actualización dinámica al cambiar selección
        playlistSelector.addEventListener('change', () => {
            const data = categoryData[playlistSelector.value];
            const statusBadge = document.getElementById('system-status-badge');
            const quoteElement = document.getElementById('category-quote');
            
            renderEst.textContent = `~ ${data.est} Horas`;
            songCountDisplay.textContent = data.songs;
            videoPotential.textContent = Math.floor(data.songs / 12);
            currentTitle.textContent = data.title;

            // Actualizar Badge y Cita
            statusBadge.textContent = `MODO ${playlistSelector.options[playlistSelector.selectedIndex].text.toUpperCase()} ACTIVADO`;
            statusBadge.style.background = "#f5f5dc";
            statusBadge.style.color = "#000";

            const quotes = {
                paz: '"En la quietud encontrarás tu fuerza."',
                fortaleza: '"Dios es nuestro amparo y fortaleza."',
                reflexion: '"Escucha la voz en el silencio."'
            };
            quoteElement.textContent = quotes[playlistSelector.value];
        });

        btnLaunch.addEventListener('click', async () => {
            const playlist = playlistSelector.value;
            const data = categoryData[playlist];
            
            btnLaunch.disabled = true;
            btnLaunch.textContent = "PRODUCCIÓN EN CURSO...";
            currentTitle.textContent = data.title;
            statusBadge.textContent = "CONECTANDO...";
            statusBadge.style.background = "#fbbf24";
            
            try {
                const response = await fetch('/run_atmos', { method: 'POST' });
                if (response.ok) {
                    statusBadge.textContent = "RENDERIZANDO EN NUBE";
                    activeProgress.style.display = "block";
                    simulateProgress(progressFill, progressText);
                } else {
                    throw new Error('Error al iniciar');
                }
            } catch (err) {
                alert('⚠️ Error: No se pudo conectar con el motor de Oracle.');
                btnLaunch.disabled = false;
                btnLaunch.textContent = "REINTENTAR";
                statusBadge.textContent = "ERROR";
            }
        });
    }
}

function simulateProgress(fill, text) {
    let progress = 0;
    const interval = setInterval(() => {
        progress += 0.5;
        fill.style.width = `${progress}%`;
        text.textContent = `${Math.floor(progress)}% completado - Procesando audio y video...`;

        if (progress >= 100) {
            clearInterval(interval);
            text.textContent = "100% - ¡Video Renderizado con Éxito!";
            document.querySelector('.status-badge').textContent = "FINALIZADO";
            document.querySelector('.status-badge').style.background = "#4ade80";
            document.getElementById('btn-launch').textContent = "NUEVA PRODUCCIÓN";
            document.getElementById('btn-launch').disabled = false;
        }
    }, 500); // Velocidad de simulación para la demo
}

function loadDashboardData() {
    // Simulando datos reales de la producción activa
    const titleElement = document.getElementById('current-title');
    titleElement.textContent = "No Temas: Yo estoy contigo en medio del valle";
}

async function loadCatalog() {
    const catalogList = document.getElementById('catalog-list');
    
    // En producción esto leería musichris_master_catalog.json
    // Por ahora, mostraremos una estructura premium
    const mockSongs = [
        { title: "Soplo de Vida", moment: "Paz Interior", bpm: 60 },
        { title: "A Medianoche", moment: "Paz Interior", bpm: 60 },
        { title: "Tu Sombra y tu Luz", moment: "Reflexión", bpm: 65 },
        { title: "Guardián", moment: "Confianza", bpm: 58 }
    ];

    catalogList.innerHTML = mockSongs.map(song => `
        <div class="catalog-item">
            <div class="song-info">
                <h3>${song.title}</h3>
                <span>${song.moment} | ${song.bpm} BPM</span>
            </div>
            <div class="actions">
                <button class="btn-action" onclick="showSongDetails('${song.title}', '${song.moment}', ${song.bpm})">Detalles</button>
                <label class="switch">
                    <input type="checkbox" checked onchange="toggleSongStatus('${song.title}')">
                    <span class="slider round"></span>
                </label>
            </div>
        </div>
    `).join('');
}

function toggleSongStatus(title) {
    console.log(`Estado de canción cambiado: ${title}`);
    // Aquí se enviaría la orden al servidor para marcarla como inactiva en el catálogo real
}

async function loadRenders() {
    const rendersGrid = document.getElementById('renders-grid');
    
    // Datos reales + Historial
    const history = [
        { title: "RENDER_ATMOS_20MIN_OFICIAL", date: "Hoy", category: "Paz Interior", duration: "00:20:00", status: "Listo" },
        { title: "Selah: Intimidad con el Padre", date: "23/04/2026", category: "Reflexión", duration: "01:05:00", status: "En YouTube" }
    ];

    rendersGrid.innerHTML = history.map(vid => `
        <div class="render-card">
            <div class="vid-thumb" style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); display: flex; align-items: center; justify-content: center;">
                <img src="./assets/app_icon.png" style="width: 60px; opacity: 0.3; filter: grayscale(1);">
                <span class="vid-tag">${vid.category}</span>
                <span class="status-tag ${vid.status === 'Listo' ? 'ready' : 'published'}">${vid.status}</span>
            </div>
            <div class="vid-info">
                <h4>${vid.title}</h4>
                <p>${vid.date} • ${vid.duration}</p>
                <div class="vid-actions">
                    <button class="btn-action" onclick="viewRender('${vid.title}')">Ver Archivo</button>
                    ${vid.status === 'Listo' ? `<button class="btn-primary-small" onclick="uploadToYoutube('${vid.title}')">SUBIR A YOUTUBE</button>` : ''}
                </div>
            </div>
        </div>
    `).join('');
}

function viewRender(title) {
    alert(`📂 Abriendo archivo de renderizado: /renders/${title}.mp4\n(En un servidor real, esto abriría el reproductor de video).`);
}

function uploadToYoutube(title) {
    const btn = event.target;
    btn.textContent = "SUBIENDO...";
    btn.disabled = true;
    
    setTimeout(() => {
        alert(`✅ ¡ÉXITO! El video '${title}' ha sido subido a YouTube con SEO optimizado.`);
        btn.textContent = "PUBLICADO";
        btn.style.background = "#4ade80";
    }, 2000);
}

function showSongDetails(title, moment, bpm) {
    alert(`🎵 FICHA TÉCNICA: ${title}\n--------------------------\nAtmósfera: ${moment}\nTempo: ${bpm} BPM\nEstado: Listado para ATMOS\n--------------------------\nPróximamente: Vista previa de audio.`);
}

// Estilos extra inyectados para el catálogo
const style = document.createElement('style');
style.textContent = `
    .catalog-list { display: flex; flex-direction: column; gap: 1rem; margin-top: 2rem; }
    .catalog-item { 
        background: var(--card-bg); 
        padding: 1.5rem; 
        border-radius: 16px; 
        display: flex; 
        justify-content: space-between; 
        align-items: center; 
        border: 1px solid var(--glass-border);
    }
    .catalog-item h3 { font-size: 1.1rem; margin-bottom: 0.2rem; }
    .catalog-item span { font-size: 0.8rem; color: var(--text-secondary); }
    .catalog-item .actions { display: flex; align-items: center; gap: 1.5rem; }
    .btn-action { 
        background: rgba(255,255,255,0.1); 
        color: white; 
        border: none; 
        padding: 0.5rem 1rem; 
        border-radius: 8px; 
        cursor: pointer;
    }

    /* Switch Styles */
    .switch {
        position: relative;
        display: inline-block;
        width: 44px;
        height: 22px;
    }
    .switch input { opacity: 0; width: 0; height: 0; }
    .slider {
        position: absolute;
        cursor: pointer;
        top: 0; left: 0; right: 0; bottom: 0;
        background-color: rgba(255,255,255,0.1);
        transition: .4s;
        border-radius: 34px;
    }
    .slider:before {
        position: absolute;
        content: "";
        height: 16px; width: 16px;
        left: 3px; bottom: 3px;
        background-color: white;
        transition: .4s;
        border-radius: 50%;
    }
    input:checked + .slider { background-color: var(--success-color); }
    input:checked + .slider:before { transform: translateX(22px); }

    .renders-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1.5rem; margin-top: 2rem; }
    .render-card { 
        background: var(--card-bg); 
        border-radius: 20px; 
        overflow: hidden; 
        border: 1px solid var(--glass-border); 
        backdrop-filter: blur(10px);
    }
    .vid-thumb { height: 160px; background: linear-gradient(45deg, #1a1a1a, #2a2a2a); position: relative; }
    .vid-tag { position: absolute; top: 10px; left: 10px; background: var(--accent-color); color: black; font-size: 0.6rem; font-weight: 800; padding: 2px 8px; border-radius: 4px; z-index: 2; }
    .status-tag { position: absolute; top: 10px; right: 10px; font-size: 0.6rem; font-weight: 700; padding: 2px 8px; border-radius: 4px; z-index: 2; }
    .status-tag.ready { background: var(--success-color); color: black; }
    .status-tag.published { background: rgba(255,255,255,0.2); color: white; }
    .vid-info { padding: 1.2rem; }
    .vid-info h4 { margin-bottom: 0.5rem; font-family: 'Playfair Display', serif; font-size: 0.9rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .vid-info p { font-size: 0.7rem; color: var(--text-secondary); margin-bottom: 1rem; }
    .vid-actions { display: flex; gap: 0.5rem; flex-direction: column; }
    .btn-primary-small { 
        background: var(--accent-color); 
        color: black; 
        border: none; 
        padding: 0.5rem; 
        border-radius: 6px; 
        font-size: 0.7rem; 
        font-weight: 700; 
        cursor: pointer; 
    }

    /* Estilos para Móviles */
    @media (max-width: 768px) {
        body { padding: 5px; }
        .dashboard-container { padding: 15px; margin-top: 5px; }
        header { 
            display: flex; 
            flex-direction: column; 
            align-items: center; 
            gap: 1.5rem; 
            padding: 20px 0;
            background: rgba(0,0,0,0.3);
            border-radius: 20px;
            margin-bottom: 20px;
        }
        .logo-area { display: flex; flex-direction: column; align-items: center; gap: 10px; }
        .logo-section h1 { font-size: 1.6rem; letter-spacing: 4px; }
        .nav-center, nav { 
            width: 90%; 
            display: flex; 
            justify-content: center; 
            gap: 0.5rem; 
            padding: 0;
        }
        .btn-nav { 
            padding: 0.6rem 1rem; 
            font-size: 0.7rem; 
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
        }
        .hero-card h2 { font-size: 1.8rem; line-height: 1.2; margin: 1.5rem 0; }
        .launch-card { padding: 1.2rem; border-radius: 24px; }
        .btn-launch { font-size: 0.9rem; letter-spacing: 1px; padding: 1.2rem; }
        .stats-grid { gap: 10px; }
        .stat-card { padding: 1rem; }
    }
`;
document.head.appendChild(style);
