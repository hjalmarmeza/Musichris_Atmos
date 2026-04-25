const fs = require('fs');
const path = require('path');
const https = require('https');

// Configuración del Proyecto y Bucket
const bucketName = 'proyecto-musichris-350df.appspot.com';
const localDirPath = path.join(__dirname, '..', 'ui', 'assets', 'Paisajes');
const outputJsonPath = path.join(__dirname, '..', 'data', 'landscapes_remote.json');

// Extraer el Token de acceso de tu config local
function getAccessToken() {
    try {
        const configPath = path.join(process.env.HOME, '.config', 'configstore', 'firebase-tools.json');
        const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
        return config.tokens.access_token;
    } catch (e) {
        console.error('❌ No se pudo leer el token de Firebase:', e.message);
        return null;
    }
}

async function uploadFile(fileName, token) {
    const filePath = path.join(localDirPath, fileName);
    const destination = `Atmos_Paisajes/${fileName}`;
    const stats = fs.statSync(filePath);
    const fileSizeInBytes = stats.size;

    return new Promise((resolve, reject) => {
        const options = {
            hostname: 'storage.googleapis.com',
            port: 443,
            path: `/upload/storage/v1/b/${bucketName}/o?uploadType=media&name=${encodeURIComponent(destination)}`,
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'video/mp4',
                'Content-Length': fileSizeInBytes
            }
        };

        const req = https.request(options, (res) => {
            let data = '';
            res.on('data', (chunk) => data += chunk);
            res.on('end', () => {
                if (res.statusCode === 200) {
                    resolve(`https://storage.googleapis.com/${bucketName}/${destination}`);
                } else {
                    reject(new Error(`Status ${res.statusCode}: ${data}`));
                }
            });
        });

        req.on('error', reject);
        fs.createReadStream(filePath).pipe(req);
    });
}

async function main() {
    const token = getAccessToken();
    if (!token) return;

    console.log('🚀 [FIREBASE-STORAGE] Iniciando carga con Token de Sesión...');
    
    if (!fs.existsSync(localDirPath)) {
        console.error('❌ Carpeta no encontrada.');
        return;
    }

    const files = fs.readdirSync(localDirPath).filter(f => f.endsWith('.mp4'));
    const landscapeMap = {};

    for (let i = 0; i < files.length; i++) {
        const fileName = files[i];
        try {
            console.log(`[${i+1}/${files.length}] ⬆️ Subiendo: ${fileName}...`);
            const url = await uploadFile(fileName, token);
            landscapeMap[fileName] = url;
            console.log(`   ✅ OK`);
        } catch (error) {
            console.error(`   ❌ Error:`, error.message);
        }
    }

    fs.writeFileSync(outputJsonPath, JSON.stringify(landscapeMap, null, 2));
    console.log(`\n🎉 CARGA COMPLETADA.`);
    console.log(`📄 Mapeo generado en: ${outputJsonPath}`);
}

main();
