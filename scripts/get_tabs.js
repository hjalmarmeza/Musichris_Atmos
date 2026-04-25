const https = require('https');

const SHEET_2_ID = '19zXfIiAZktXXyixZ1HdcW1IO9bOBn8S8sRPZAXUVZbE';

async function getTabs() {
    const url = `https://docs.google.com/spreadsheets/d/${SHEET_2_ID}/gviz/tq?tqx=out:json`;
    https.get(url, (res) => {
        let data = '';
        res.on('data', (chunk) => data += chunk);
        res.on('end', () => {
            // El gviz API a veces no da los nombres de las pestañas directamente en el JSON principal de datos.
            // Pero podemos intentar acceder por el feed de metadatos o simplemente probar las que conocemos.
            console.log("📡 Metadata de Sheets recibida. Analizando estructura...");
            console.log(data.substring(0, 500)); // Ver si hay pistas en el encabezado
        });
    });
}

getTabs();
