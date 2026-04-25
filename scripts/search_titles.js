const https = require('https');

const SHEET_2_ID = '19zXfIiAZktXXyixZ1HdcW1IO9bOBn8S8sRPZAXUVZbE';

async function searchAll() {
    const url = `https://docs.google.com/spreadsheets/d/${SHEET_2_ID}/gviz/tq?tqx=out:json&sheet=Hoja 2`;
    https.get(url, (res) => {
        let data = '';
        res.on('data', (chunk) => data += chunk);
        res.on('end', () => {
            const jsonStr = data.substring(data.indexOf('(') + 1, data.lastIndexOf(')'));
            const rows = JSON.parse(jsonStr).table.rows;
            
            console.log(`🔎 Total filas en Sheet 2: ${rows.length}`);
            
            const find = (name) => {
                const found = rows.find(r => r.c[2] && r.c[2].v.toLowerCase().includes(name.toLowerCase()));
                if (found) {
                    console.log(`✅ ENCONTRADO: "${name}" -> Tituló real: "${found.c[2].v}"`);
                } else {
                    console.log(`❌ NO ENCONTRADO: "${name}"`);
                }
            };

            find("José");
            find("María");
            find("Cireneo");
            find("Emmanuel");
        });
    });
}

searchAll();
