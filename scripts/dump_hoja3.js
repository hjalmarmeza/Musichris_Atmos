const https = require('https');

const SHEET_2_ID = '19zXfIiAZktXXyixZ1HdcW1IO9bOBn8S8sRPZAXUVZbE';

async function dumpHoja3() {
    const url = `https://docs.google.com/spreadsheets/d/${SHEET_2_ID}/gviz/tq?tqx=out:json&sheet=Hoja 3`;
    https.get(url, (res) => {
        let data = '';
        res.on('data', (chunk) => data += chunk);
        res.on('end', () => {
            const jsonStr = data.substring(data.indexOf('(') + 1, data.lastIndexOf(')'));
            const rows = JSON.parse(jsonStr).table.rows;
            
            console.log(`📊 Total filas en Hoja 3: ${rows.length}`);
            
            // Ver una muestra de la mitad y del final
            const sample = [0, 1, 2, 50, 100, 200, 300, 400];
            sample.forEach(i => {
                if (rows[i]) {
                    const cols = rows[i].c.map(c => c ? c.v : 'NULL').join(' | ');
                    console.log(`${i}: ${cols}`);
                }
            });
        });
    });
}

dumpHoja3();
