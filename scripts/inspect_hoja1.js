const https = require('https');

const SHEET_2_ID = '19zXfIiAZktXXyixZ1HdcW1IO9bOBn8S8sRPZAXUVZbE';

async function checkHoja1() {
    const url = `https://docs.google.com/spreadsheets/d/${SHEET_2_ID}/gviz/tq?tqx=out:json&sheet=Hoja 1`;
    https.get(url, (res) => {
        let data = '';
        res.on('data', (chunk) => data += chunk);
        res.on('end', () => {
            const jsonStr = data.substring(data.indexOf('(') + 1, data.lastIndexOf(')'));
            const rows = JSON.parse(jsonStr).table.rows.slice(0, 50); // Ver las primeras 50
            
            rows.forEach((r, i) => {
                const title = r.c[2] ? r.c[2].v : 'NULL';
                console.log(`${i}: ${title}`);
            });
        });
    });
}

checkHoja1();
