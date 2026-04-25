const https = require('https');

const SHEET_2_ID = '19zXfIiAZktXXyixZ1HdcW1IO9bOBn8S8sRPZAXUVZbE';

async function inspectHoja2VeryStart() {
    const url = `https://docs.google.com/spreadsheets/d/${SHEET_2_ID}/gviz/tq?tqx=out:json&sheet=Hoja 2`;
    https.get(url, (res) => {
        let data = '';
        res.on('data', (chunk) => data += chunk);
        res.on('end', () => {
            const jsonStr = data.substring(data.indexOf('(') + 1, data.lastIndexOf(')'));
            const rows = JSON.parse(jsonStr).table.rows.slice(0, 15);
            
            rows.forEach((r, i) => {
                const cols = r.c.map(c => c ? c.v : 'NULL').join(' | ');
                console.log(`${i}: ${cols}`);
            });
        });
    });
}

inspectHoja2VeryStart();
