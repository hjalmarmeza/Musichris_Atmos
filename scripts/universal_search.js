const https = require('https');

const SHEET_2_ID = '19zXfIiAZktXXyixZ1HdcW1IO9bOBn8S8sRPZAXUVZbE';

async function universalSearch(name) {
    const tabs = ["Hoja 1", "Hoja 2", "Hoja 3", "Hoja 4"];
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
                        const found = rows.find(r => r.c && JSON.stringify(r.c).toLowerCase().includes(name.toLowerCase()));
                        if (found) {
                            console.log(`🎯 ¡ENCONTRADO en "${tab}"!`);
                            console.log(`Datos: ${JSON.stringify(found.c.map(c => c ? c.v : 'NULL'))}`);
                        }
                    } catch (e) {}
                    resolve();
                });
            });
        });
    }
}

universalSearch("Sueño");
