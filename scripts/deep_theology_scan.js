const https = require('https');

const SHEET_1_ID = '1oTVSF7CjrCtnk3pHdBIRE8gzhE9zKDM5NJFyWV-qsJs';

async function checkTheologyTabs() {
    const tabs = ["Hoja 1", "Hoja 2", "Hoja 3", "Hoja 4", "Canciones Suno", "Suno Audio"];
    for (const tab of tabs) {
        const url = `https://docs.google.com/spreadsheets/d/${SHEET_1_ID}/gviz/tq?tqx=out:json&sheet=${encodeURIComponent(tab)}`;
        await new Promise((resolve) => {
            https.get(url, (res) => {
                let data = '';
                res.on('data', (chunk) => data += chunk);
                res.on('end', () => {
                    try {
                        const jsonStr = data.substring(data.indexOf('(') + 1, data.lastIndexOf(')'));
                        const rows = JSON.parse(jsonStr).table.rows;
                        console.log(`📊 Pestaña "${tab}": ${rows.length} filas.`);
                        
                        // Buscar URLs (algo que empiece por http)
                        const sampleRow = rows.find(r => r.c && r.c.some(c => c && c.v && c.v.toString().startsWith("http")));
                        if (sampleRow) {
                            console.log(`🎯 ¡URLs ENCONTRADAS EN "${tab}"!`);
                            const jose = rows.find(r => r.c && JSON.stringify(r.c).toLowerCase().includes("josé"));
                            if (jose) console.log(`✅ José está aquí: ${JSON.stringify(jose.c.map(c => c ? c.v : 'NULL'))}`);
                        }
                    } catch (e) {
                        // Ignorar errores de pestañas inexistentes
                    }
                    resolve();
                });
            });
        });
    }
}

checkTheologyTabs();
