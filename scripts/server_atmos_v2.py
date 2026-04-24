from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv('/home/ubuntu/.env')

app = Flask(__name__)
CORS(app)

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_REPO = "Antigravity"
GITHUB_OWNER = "hjalmarmeza"
HISTORY_FILE = '/home/ubuntu/production_history.json'

def save_to_history(data):
    history = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r') as f:
                history = json.load(f)
        except: pass
    
    data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    history.insert(0, data) # El más reciente primero
    
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history[:50], f) # Guardar los últimos 50

@app.route('/status', methods=['GET'])
def status():
    return jsonify({"status": "online", "message": "MusiChris Atmos Control Center is ready."})

@app.route('/history', methods=['GET'])
def get_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            return jsonify(json.load(f))
    return jsonify([])

@app.route('/process', methods=['POST'])
def process():
    data = request.json
    song_url = data.get('song_url')
    theme = data.get('theme', 'Cinematic')
    
    if not song_url:
        return jsonify({"error": "Missing song URL"}), 400

    # Disparar GitHub Action
    url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/dispatches"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    payload = {
        "event_type": "atmos_trigger",
        "client_payload": {
            "song_url": song_url,
            "theme": theme
        }
    }
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 204:
        save_to_history({"song_url": song_url, "theme": theme, "status": "Queued in Cloud"})
        return jsonify({
            "status": "success", 
            "message": "Render sequence initiated in GitHub Cloud."
        })
    else:
        return jsonify({
            "status": "error", 
            "message": f"GitHub rejection: {response.text}"
        }), response.status_code

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
