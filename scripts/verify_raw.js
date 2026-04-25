const https = require('https');

const SHEET_1_ID = '1oTVSF7CjrCtnk3pHdBIRE8gzhE9zKDM5NJFyWV-qsJs';
const SHEET_2_ID = '19zXfIiAZktXXyixZ1HdcW1IO9bOBn8S8sRPZAXUVZbE';

async function fetchRaw(id, sheetName) {
    const url = `https://docs.google.com/spreadsheets/d/${id}/gviz/tq?tqx=out:json&sheet=${encodeURIComponent(sheetName)}`;
    return new Promise((resolve) => {
        https.get(url, (res) => {
            let data = '';
            res.on('data', (chunk) => data += chunk);
            res.on('end', () => {
                const jsonStr = data.substring(data.indexOf('(') + 1, data.lastIndexOf(')'));
                resolve(JSON.parse(jsonStr).table.rows.slice(0, 10)); // Solo las primeras 10 para comparar
            });
        });
    });
}

async function check() {
    const theology = await fetchRaw(SHEET_1_ID, 'Hoja 4');
    const urls = await fetchRaw(SHEET_2_ID, 'Hoja 2');

    console.log("📄 MUESTRA SHEET 1 (TEOLOGÍA):");
    theology.forEach((r, i) => console.log(`${i}: ${r.c[1] ? r.c[1].v : 'NULL'}`));

    console.log("\n📄 MUESTRA SHEET 2 (URLS):");
    urls.forEach((r, i) => console.log(`${i}: ${r.c[2] ? r.c[2].v : 'NULL'}`));
}

check();
