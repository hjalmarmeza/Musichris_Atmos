const https = require('https');

const SHEET_2_ID = '19zXfIiAZktXXyixZ1HdcW1IO9bOBn8S8sRPZAXUVZbE';

async function dumpOtherTabs() {
    const tabs = ["Hoja 1", "Hoja 4"];
    for (const tab of tabs) {
        const url = `https://docs.google.com/spreadsheets/d/${SHEET_2_ID}/gviz/tq?tqx=out:json&sheet=${encodeURIComponent(tab)}`;
        await new Promise((resolve) => {
            https.get(url, (res) => {
                let data = '';
                res.on('data', (chunk) => data += chunk);
                res.on('end', () => {
                    try {
                        const jsonStr = data.substring(data.indexOf('(') + 1, data.lastIndexOf(')'));
                        const rows = JSON.parse(jsonStr).table.rows;
                        console.log(`--- Pestaña: ${tab} (Filas: ${rows.length}) ---`);
                        rows.slice(0, 10).forEach((r, i) => {
                            const cols = r.c ? r.c.map(c => c ? c.v : 'NULL').join(' | ') : 'EMPTY';
                            console.log(`${i}: ${cols}`);
                        });
                    } catch (e) {
                        console.log(`Error en ${tab}: ${e.message}`);
                    }
                    resolve();
                });
            });
        });
    }
}

dumpOtherTabs();
