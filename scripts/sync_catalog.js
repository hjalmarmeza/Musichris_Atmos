const fs = require('fs');
const https = require('https');

const SHEET_1_ID = '1oTVSF7CjrCtnk3pHdBIRE8gzhE9zKDM5NJFyWV-qsJs';
const SHEET_2_ID = '19zXfIiAZktXXyixZ1HdcW1IO9bOBn8S8sRPZAXUVZbE';

// MAPA DE SINÓNIMOS DEFINITIVO (Basado en diagnóstico real)
const SYNONYMS = {
    'refugio seguro': 'la torre mas alta',
    'la voz de jehova': 'voz de jehova',
    'quien mas': 'quien mas',
    'nada me faltara': 'mi pastor y mi rey',
    'pelea por mi': 'pelea por mi.',
    'levantate': 'levantate',
    'que es el hombre': 'que es el hombre',
    'roca y escudo (medley)': 'roca y escudo',
    'canto y musica': 'cantico nuevo',
    'desde el principio': 'desde siempre',
    'fuerza mia': 'mi roca firme',
    'la belleza de tu gloria (instrumental)': 'la mejor parte',
    'emmanuel': 'emmanuel (suno)',
    'el si de maria': 'el si de maria',
    'el sueño de jose': 'el sueño de jose (suno)',
    'la travesia tranquila': 'la travesia tranquila (suno)',
    'la noche rota': 'la noche rota (suno)',
    'la ofrenda real': 'la ofrenda real (suno)',
    'en un humilde pesebre': 'en un humilde pesebre (suno)'
};

function normalize(text) {
    if (!text) return '';
    return text.toString().toLowerCase()
        .normalize('NFD').replace(/[\u0300-\u036f]/g, '') // Quitar acentos
        .replace(/[^\w\s]/gi, '') // QUITAR TODO LO QUE NO SEA LETRA O ESPACIO (Puntos, comas, signos)
        .trim();
}

async function fetchSheetData(id, sheetName) {
    const url = `https://docs.google.com/spreadsheets/d/${id}/gviz/tq?tqx=out:json&sheet=${encodeURIComponent(sheetName)}`;
    return new Promise((resolve, reject) => {
        https.get(url, (res) => {
            let data = '';
            res.on('data', (chunk) => data += chunk);
            res.on('end', () => {
                const jsonStr = data.substring(data.indexOf('(') + 1, data.lastIndexOf(')'));
                resolve(JSON.parse(jsonStr).table.rows);
            });
        }).on('error', reject);
    });
}

async function buildCatalog() {
    console.log("🛰️ Iniciando Triangulación Maestra v2.0...");
    
    try {
        const rowsTheology = await fetchSheetData(SHEET_1_ID, 'Hoja 4');
        const rowsUrls = await fetchSheetData(SHEET_2_ID, 'Hoja 2');

        const urlMap = {};
        rowsUrls.forEach(r => {
            const title = r.c[2] ? r.c[2].v : '';
            const url = r.c[3] ? r.c[3].v : '';
            if (title && url) {
                const norm = normalize(title);
                // Si hay una v2, la preferimos si la v1 ya existe
                if (!urlMap[norm] || title.includes('v2')) {
                    urlMap[norm] = url;
                }
            }
        });

        const usedUrls = new Set();
        const catalog = rowsTheology.map(r => {
            const clean = (i) => (r.c[i] ? r.c[i].v : '');
            const title = clean(1);
            if (!title || title.length > 70 || title.includes('Style')) return null;

            const normTitle = normalize(title);
            let songUrl = urlMap[normTitle];

            // Probar sinónimos si no hay match
            if (!songUrl && SYNONYMS[normTitle]) {
                const synNorm = normalize(SYNONYMS[normTitle]);
                songUrl = urlMap[synNorm];
            }

            if (songUrl) {
                // Marcar como usado (usamos el nombre normalizado que hizo el match)
                if (urlMap[normTitle]) usedUrls.add(normTitle);
                else usedUrls.add(normalize(SYNONYMS[normTitle]));
            } else {
                console.warn(`⚠️ Sin URL: ${title}`);
            }

            return {
                title: title,
                audio_url: songUrl || "",
                moments: [clean(6) || "General"],
                context: {
                    verse: clean(2),
                    theme: clean(4),
                    focus: clean(3),
                    bpm: parseInt(clean(5)) || 70
                }
            };
        }).filter(s => s !== null && s.audio_url !== "");

        const unused = Object.keys(urlMap).filter(k => !usedUrls.has(k));
        console.log(`📡 URLs no utilizadas (${unused.length}): ${unused.slice(0, 15).join(', ')}...`);

        fs.writeFileSync('/Users/hjalmarmeza/Downloads/Antigravity/Musichris_Atmos/data/musichris_master_catalog.json', JSON.stringify(catalog, null, 2));
        console.log(`✅ ¡Misión Cumplida! ${catalog.length} canciones sincronizadas.`);
    } catch (e) {
        console.error("❌ Error en la triangulación:", e);
    }
}

buildCatalog();
