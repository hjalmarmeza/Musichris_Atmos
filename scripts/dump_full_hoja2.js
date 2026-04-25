const https = require('https');

const SHEET_2_ID = '19zXfIiAZktXXyixZ1HdcW1IO9bOBn8S8sRPZAXUVZbE';

async function dumpFullHoja2() {
    const url = `https://docs.google.com/spreadsheets/d/${SHEET_2_ID}/gviz/tq?tqx=out:json&sheet=Hoja 2`;
    https.get(url, (res) => {
        let data = '';
        res.on('data', (chunk) => data += chunk);
        res.on('end', () => {
            const jsonStr = data.substring(data.indexOf('(') + 1, data.lastIndexOf(')'));
            const rows = JSON.parse(jsonStr).table.rows;
            
            let output = `Total filas: ${rows.length}\n`;
            rows.forEach((r, i) => {
                const cols = r.c.map(c => c ? c.v : 'NULL').join(' | ');
                output += `${i}: ${cols}\n`;
            });
            
            require('fs').writeFileSync('/Users/hjalmarmeza/Downloads/Antigravity/Musichris_Atmos/scripts/full_hoja2_dump.txt', output);
            console.log(`✅ Volcado completo en full_hoja2_dump.txt`);
        });
    });
}

dumpFullHoja2();
