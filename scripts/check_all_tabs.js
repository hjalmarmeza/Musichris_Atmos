const https = require('https');

const SHEET_2_ID = '19zXfIiAZktXXyixZ1HdcW1IO9bOBn8S8sRPZAXUVZbE';

async function checkTab(name) {
    const url = `https://docs.google.com/spreadsheets/d/${SHEET_2_ID}/gviz/tq?tqx=out:json&sheet=${encodeURIComponent(name)}`;
    return new Promise((resolve) => {
        https.get(url, (res) => {
            let data = '';
            res.on('data', (chunk) => data += chunk);
            res.on('end', () => {
                try {
                    const jsonStr = data.substring(data.indexOf('(') + 1, data.lastIndexOf(')'));
                    const rows = JSON.parse(jsonStr).table.rows;
                    console.log(`📊 Pestaña "${name}": ${rows.length} filas.`);
                    // Buscar a José o María
                    const found = rows.find(r => r.c[2] && r.c[2].v.toLowerCase().includes("josé"));
                    if (found) console.log(`🎯 ¡ENCONTRADOS EN ${name}!`);
                } catch (e) {
                    console.log(`❌ Pestaña "${name}" no existe o está vacía.`);
                }
                resolve();
            });
        });
    });
}

async function run() {
    await checkTab("Hoja 1");
    await checkTab("Hoja 2");
    await checkTab("Hoja 3");
    await checkTab("Navidad");
    await checkTab("Suno");
    await checkTab("Canciones Suno");
}

run();
