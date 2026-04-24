from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

load_dotenv('/home/ubuntu/.env')

app = Flask(__name__)
CORS(app)

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_REPO = "hjalmarmeza/Antigravity" # Ajustar si el repo es diferente
GITHUB_OWNER = "hjalmarmeza"

@app.route('/status', methods=['GET'])
def status():
    return jsonify({"status": "online", "message": "MusiChris Atmos Control Center is ready."})

@app.route('/process', methods=['POST'])
def process():
    data = request.json
    song_url = data.get('song_url')
    theme = data.get('theme', 'Cinematic')
    
    if not song_url:
        return jsonify({"error": "Missing song URL"}), 400

    # Disparar GitHub Action vía Repository Dispatch
    url = f"https://api.github.com/repos/{GITHUB_OWNER}/Antigravity/dispatches"
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
        return jsonify({
            "status": "success", 
            "message": "Render sequence initiated in GitHub Cloud. Check YouTube in 15 mins."
        })
    else:
        return jsonify({
            "status": "error", 
            "message": f"GitHub rejection: {response.text}"
        }), response.status_code

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
