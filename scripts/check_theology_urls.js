const https = require('https');

const SHEET_1_ID = '1oTVSF7CjrCtnk3pHdBIRE8gzhE9zKDM5NJFyWV-qsJs';

async function checkTheologyHoja2() {
    const url = `https://docs.google.com/spreadsheets/d/${SHEET_1_ID}/gviz/tq?tqx=out:json&sheet=Hoja 2`;
    https.get(url, (res) => {
        let data = '';
        res.on('data', (chunk) => data += chunk);
        res.on('end', () => {
            try {
                const jsonStr = data.substring(data.indexOf('(') + 1, data.lastIndexOf(')'));
                const rows = JSON.parse(jsonStr).table.rows;
                console.log(`📊 Hoja 2 del archivo teológico: ${rows.length} filas.`);
                
                // Buscar a José o María
                const found = rows.find(r => r.c && JSON.stringify(r.c).toLowerCase().includes("josé"));
                if (found) {
                    console.log(`🎯 ¡ENCONTRADOS! Están en la Hoja 2 del primer archivo.`);
                    console.log(`Muestra: ${JSON.stringify(found.c.map(c => c ? c.v : 'NULL'))}`);
                } else {
                    console.log(`❌ Tampoco están aquí.`);
                }
            } catch (e) {
                console.log(`❌ Error al leer Hoja 2 del primer archivo.`);
            }
        });
    });
}

checkTheologyHoja2();
