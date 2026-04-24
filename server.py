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
                
                # Definir Grupos Maestros
                groups = {
                    "Paz & Reposo": ["Paz Interior", "Paz / Confianza (\"Raphah\")", "Paz / Meditación / Descanso", "Refugio / Seguridad", "Descanso / Hogar espiritual", "Quietud / Confianza Silenciosa", "Vigilancia divina / Descanso seguro", "Voz de Dios / Calma", "Seguridad y Paz en Dios", "Alivio / Refugio Inmersivo"],
                    "Guerra & Fortaleza": ["Guerra Espiritual", "Poder y Fortaleza", "Victoria Final", "Fortaleza y Agilidad Divina", "Valentía / Confianza en medio del peligro", "Protección / Poder", "Seguridad en la Defensa Divina", "Refugio activo / Protección en la guerra", "Inmunidad divina / Protección sobrenatural"],
                    "Adoración & Intimidad": ["Adoración celestial", "Adoración extravagante / Perdón", "Intimidad de madrugada / Sed del alma", "Santidad de Dios", "Selah", "Anhelo / Contemplación", "Prioridad / Presencia", "Omnipresencia / Intimidad Total", "La Paternidad de Dios"],
                    "Victoria & Gozo": ["Victoria & Gozo", "Victoria / Fe activa", "Celebración Colectiva", "Gratitud y Exaltación", "Joyful", "El Gozo como Regalo Divino", "Victoria y Gratitud", "La Victoria y el Desfile Divino"],
                    "Avivamiento & Gracia": ["Avivamiento / Restauración", "Restauración / Gracia", "Redención completa", "Sed espiritual / Renovación", "La respuesta natural al perdón es la adoración pública", "La confianza en que la bondad de Dios supera el error"]
                }
                
                stats = {k: 0 for k in groups.keys()}
                for s in catalog:
                    if s['title'] in disabled_songs: continue
                    
                    # Buscar en qué grupo encaja la canción
                    song_tags = set(s.get('moments', []))
                    song_tags.add(s.get('theme', ''))
                    
                    for group_name, patterns in groups.items():
                        if any(p in song_tags for p in patterns):
                            stats[group_name] += 1
                
                # Eliminar grupos vacíos (opcional)
                stats = {k: v for k, v in stats.items() if v > 0}
                
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
