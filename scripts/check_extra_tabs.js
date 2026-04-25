const https = require('https');

const SHEET_2_ID = '19zXfIiAZktXXyixZ1HdcW1IO9bOBn8S8sRPZAXUVZbE';

async function checkTab(name) {
    const url = `https://docs.google.com/spreadsheets/d/${SHEET_2_ID}/gviz/tq?tqx=out:json&sheet=${encodeURIComponent(name)}`;
    https.get(url, (res) => {
        let data = '';
        res.on('data', (chunk) => data += chunk);
        res.on('end', () => {
            try {
                const jsonStr = data.substring(data.indexOf('(') + 1, data.lastIndexOf(')'));
                const rows = JSON.parse(jsonStr).table.rows;
                console.log(`📊 Pestaña "${name}": ${rows.length} filas.`);
                
                const found = rows.find(r => r.c && JSON.stringify(r.c).toLowerCase().includes("josé"));
                if (found) {
                    console.log(`🎯 ¡ENCONTRADOS EN ${name}!`);
                    console.log(`Fila: ${JSON.stringify(found.c.map(c => c ? c.v : 'NULL'))}`);
                }
            } catch (e) {
                console.log(`❌ Error en "${name}"`);
            }
        });
    });
}

checkTab("Canciones Iniciales");
checkTab("Suno Audio");
checkTab("Hoja 4");
checkTab("Navidad");
