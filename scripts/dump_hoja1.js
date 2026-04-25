const https = require('https');

const SHEET_2_ID = '19zXfIiAZktXXyixZ1HdcW1IO9bOBn8S8sRPZAXUVZbE';

async function dumpHoja1() {
    const url = `https://docs.google.com/spreadsheets/d/${SHEET_2_ID}/gviz/tq?tqx=out:json&sheet=Hoja 1`;
    https.get(url, (res) => {
        let data = '';
        res.on('data', (chunk) => data += chunk);
        res.on('end', () => {
            const jsonStr = data.substring(data.indexOf('(') + 1, data.lastIndexOf(')'));
            const rows = JSON.parse(jsonStr).table.rows;
            console.log(`--- Pestaña: Hoja 1 (Filas: ${rows.length}) ---`);
            rows.slice(0, 20).forEach((r, i) => {
                const cols = r.c ? r.c.map(c => c ? c.v : 'NULL').join(' | ') : 'EMPTY';
                console.log(`${i}: ${cols}`);
            });
        });
    });
}

dumpHoja1();
