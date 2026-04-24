import http.server
import socketserver
import subprocess
import os
import json

PORT = 8080

class AtmosHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/stats':
            try:
                catalog_path = '../data/musichris_master_catalog.json'
                disabled_path = '../data/disabled_songs.json'
                if not os.path.exists(catalog_path): catalog_path = 'data/musichris_master_catalog.json'
                if not os.path.exists(disabled_path): disabled_path = 'data/disabled_songs.json'
                
                with open(catalog_path, 'r') as f:
                    catalog = json.load(f)
                
                disabled_songs = []
                if os.path.exists(disabled_path):
                    with open(disabled_path, 'r') as f:
                        disabled_songs = json.load(f)
                
                stats = {}
                for s in catalog:
                    if s['title'] in disabled_songs: continue
                    # Combinar Moments y Theme para máxima variedad
                    tags = set(s.get('moments', []))
                    theme = s.get('theme', '')
                    if theme and len(theme) > 2 and 'Guitarra' not in theme: # Filtro técnico
                        tags.add(theme)
                    
                    for t in tags:
                        stats[t] = stats.get(t, 0) + 1
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(stats).encode())
            except Exception as e:
                self.send_error(500, str(e))
        elif self.path == '/catalog':
            try:
                catalog_path = '../data/musichris_master_catalog.json'
                disabled_path = '../data/disabled_songs.json'
                if not os.path.exists(catalog_path): catalog_path = 'data/musichris_master_catalog.json'
                if not os.path.exists(disabled_path): disabled_path = 'data/disabled_songs.json'
                
                with open(catalog_path, 'r') as f:
                    catalog = json.load(f)
                
                disabled_songs = []
                if os.path.exists(disabled_path):
                    with open(disabled_path, 'r') as f:
                        disabled_songs = json.load(f)
                
                for s in catalog:
                    s['disabled'] = s['title'] in disabled_songs
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(catalog).encode())
            except Exception as e:
                self.send_error(500, str(e))
        elif self.path == '/toggle_song':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = json.loads(self.rfile.read(content_length).decode('utf-8'))
                title = post_data.get('title')
                disabled = post_data.get('disabled')
                
                disabled_path = '../data/disabled_songs.json'
                if not os.path.exists(disabled_path): 
                    disabled_songs = []
                else:
                    with open(disabled_path, 'r') as f:
                        disabled_songs = json.load(f)
                
                if disabled and title not in disabled_songs:
                    disabled_songs.append(title)
                elif not disabled and title in disabled_songs:
                    disabled_songs.remove(title)
                
                with open(disabled_path, 'w') as f:
                    json.dump(disabled_songs, f)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'ok'}).encode())
            except Exception as e:
                self.send_error(500, str(e))
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == '/run_atmos':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = json.loads(self.rfile.read(content_length).decode('utf-8'))
                
                duration = post_data.get('duration', 3600)
                theme = post_data.get('theme', 'Paz Interior')
                
                # Ejecutar motor con argumentos
                subprocess.Popen(['python3', '../scripts/atmos_engine.py', str(duration), theme])
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'Production Started', 'theme': theme, 'duration': duration}).encode())
            except Exception as e:
                self.send_error(500, str(e))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

# Ajustar directorio para que funcione en cualquier entorno
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.join(script_dir, 'ui'))

with socketserver.TCPServer(('', PORT), AtmosHandler) as httpd:
    print(f'🚀 MusiChris Atmos Server en puerto {PORT}')
    httpd.serve_forever()
