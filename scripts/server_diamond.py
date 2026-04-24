from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Detectar entorno y configurar rutas
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, '.env'))

app = Flask(__name__)
CORS(app)

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_REPO = "Antigravity"
GITHUB_OWNER = "hjalmarmeza"

# Rutas de Archivos
CATALOG_PATH = os.path.join(BASE_DIR, 'data/musichris_master_catalog.json')
DISABLED_PATH = os.path.join(BASE_DIR, 'data/disabled_songs.json')
HISTORY_FILE = os.path.join(BASE_DIR, 'data/production_history.json')

def get_disabled_songs():
    if os.path.exists(DISABLED_PATH):
        try:
            with open(DISABLED_PATH, 'r') as f:
                return json.load(f)
        except: return []
    return []

@app.route('/catalog', methods=['GET'])
def get_catalog():
    if not os.path.exists(CATALOG_PATH):
        return jsonify({"error": "Catalog not found"}), 404
        
    with open(CATALOG_PATH, 'r') as f:
        catalog = json.load(f)
    
    disabled = get_disabled_songs()
    for s in catalog:
        s['disabled'] = s['title'] in disabled
    
    return jsonify(catalog)

@app.route('/stats', methods=['GET'])
def get_stats():
    if not os.path.exists(CATALOG_PATH): return jsonify({})
    
    with open(CATALOG_PATH, 'r') as f:
        catalog = json.load(f)
    
    disabled = get_disabled_songs()
    
    # Categorías principales según MusiChris Atmos
    stats = {"Confianza": 0, "Paz": 0, "Victoria": 0, "Guerra": 0}
    
    for s in catalog:
        if s['title'] in disabled: continue
        
        # Mapeo inteligente por palabras clave en tema o momentos
        txt = f"{s.get('theme','')} {' '.join(s.get('moments', []))}".lower()
        if any(w in txt for w in ["confianza", "fe", "creer"]): stats["Confianza"] += 1
        if any(w in txt for w in ["paz", "descanso", "calma", "quietud"]): stats["Paz"] += 1
        if any(w in txt for w in ["victoria", "gozo", "celebracion"]): stats["Victoria"] += 1
        if any(w in txt for w in ["guerra", "poder", "batalla"]): stats["Guerra"] += 1

    ready = {k: v >= 10 for k, v in stats.items()} # Se necesitan al menos 10 canciones por categoría
    return jsonify({"stats": stats, "ready": ready})

@app.route('/toggle_song', methods=['POST'])
def toggle_song():
    data = request.json
    title = data.get('title')
    disabled_state = data.get('disabled')
    
    disabled_songs = get_disabled_songs()
    
    if disabled_state and title not in disabled_songs:
        disabled_songs.append(title)
    elif not disabled_state and title in disabled_songs:
        disabled_songs.remove(title)
        
    with open(DISABLED_PATH, 'w') as f:
        json.dump(disabled_songs, f)
        
    return jsonify({"status": "ok"})

@app.route('/history', methods=['GET'])
def get_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            return jsonify(json.load(f))
    return jsonify([])

@app.route('/process', methods=['POST'])
def process():
    data = request.json
    theme = data.get('theme', 'Confianza')
    duration = data.get('duration', 3600)  # Default 1h
    style = data.get('style', 'humo')
    
    # Log para auditoría
    print(f"🚀 Iniciando producción: {theme} | {duration}s | Estilo: {style}")

    # Notificar a GitHub Actions
    url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/dispatches"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    payload = {
        "event_type": "atmos_render",
        "client_payload": {
            "theme": theme,
            "duration": duration,
            "style": style
        }
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 204:
            # Guardar en historial
            history = []
            if os.path.exists(HISTORY_FILE):
                with open(HISTORY_FILE, 'r') as f: history = json.load(f)
            
            history.insert(0, {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "theme": theme,
                "duration": duration,
                "style": style
            })
            with open(HISTORY_FILE, 'w') as f: json.dump(history[:20], f) # Mantener últimos 20
            return jsonify({"status": "success", "message": "Signal sent to GitHub"}), 200
        else:
            return jsonify({"status": "error", "message": response.text}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/status', methods=['GET'])
def status():
    return jsonify({"status": "online", "message": "MusiChris Atmos Control Center V6.2 Running"})

if __name__ == '__main__':
    # Usar puerto 5000 por defecto para Flask
    app.run(host='0.0.0.0', port=5000)
